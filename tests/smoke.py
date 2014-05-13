#!/usr/bin/env python
#
"""smoke
    Runs a smoke test of the jahmon installation on mini-mon by ensuring
    metrics are flowing and creating a new notification, alarm and that the
    Threshold Engine changes the state of the alarm.  This requires the mon
    CLI and must be run on one of the mini-mon VMs. Tested running on kafka VM.
    Get it by following the instructions on
    https://wiki.hpcloud.net/display/iaas/Monitoring+CLI.
    If you want to see the notification, you must install postfix on the kakfa
    VM, configure it to be local, and modify /etc/mon/notification.yaml to use
    localhost for the email server, then restart

    TODO:
        1. Add check of notification history when that is implemented
        2. Add check of mail getting to root when postfix is added mini-mon.
           This script will have to run on the kafka VM
"""

from __future__ import print_function
import json
import sys
import os
import subprocess
import time


# export OS_AUTH_TOKEN=82510970543135
# export OS_NO_CLIENT_AUTH=1
# export MON_API_URL=http://192.168.10.4:8080/v2.0/

os.environ['OS_AUTH_TOKEN'] = '82510970543135'
os.environ['OS_NO_CLIENT_AUTH'] = '1'
os.environ['MON_API_URL'] = 'http://192.168.10.4:8080/v2.0/'


def change_alarm_state(alarm_id, new_state):
    print('Changing Alarm state to %s' % new_state)
    result_json = run_mon_cli(['alarm-patch', '--state', new_state, alarm_id])
    if result_json['state'] != new_state:
        print('Alarm patch failed, expected state of %s but was %s' %
              (result_json['state'], new_state), file=sys.stderr)
        return 1


def get_alarm_state(alarm_id):
    result_json = run_mon_cli(['alarm-show', alarm_id])
    return result_json['state']


def check_alarm_history(alarm_id, states):
    transitions = len(states) - 1
    print('Checking Alarm History')
    # May take some time for Alarm history to flow all the way through
    for _ in range(0, 10):
        result_json = run_mon_cli(['alarm-history', alarm_id])
        if len(result_json) >= transitions:
            break
        time.sleep(4)

    result = True
    if not check_expected(transitions, len(result_json),
                          'number of history entries'):
        return False
    result_json.sort(key=lambda x: x['timestamp'])
    for i in range(0, transitions):
        old_state = states[i]
        new_state = states[i+1]
        alarm_json = result_json[i]
        if not check_expected(old_state, alarm_json['old_state'], 'old_state'):
            result = False
        if not check_expected(new_state, alarm_json['new_state'], 'new_state'):
            result = False
        if not check_expected(alarm_id, alarm_json['alarm_id'], 'alarm_id'):
            result = False

    if result:
        print('Alarm History is OK')
    return result


def check_expected(expected, actual, what):
    if (expected == actual):
        return True
    print("Incorrect value for alarm history %s expected '%s' but was '%s'" %
          (what, str(expected), str(actual)), file=sys.stderr)
    return False


def create_alarm(name, expression, notification_method_id, description=None):
    args = ['alarm-create']
    if (description):
            args.append('--description')
            args.append(description)
    args.append('--alarm-actions')
    args.append(notification_method_id)
    args.append('--ok-actions')
    args.append(notification_method_id)
    args.append('--undetermined-actions')
    args.append(notification_method_id)
    args.append(name)
    args.append(expression)
    print('Creating alarm')
    result_json = run_mon_cli(args)

    # Parse out id
    alarm_id = result_json['id']
    return alarm_id


def get_metrics(name, dimensions):
    print('Getting metrics for %s ' % (name + str(dimensions)))
    dimensions_arg = ''
    for key, value in dimensions.iteritems():
        if dimensions_arg != '':
            dimensions_arg = dimensions_arg + ','
        dimensions_arg = dimensions_arg + key + '=' + value
    return run_mon_cli(['measurement-list', '--dimensions',
                          dimensions_arg, name, '00'])


def run_mon_cli(args, useJson=True):
    if useJson:
        args.insert(0, '--json')
    args.insert(0, 'mon')
    try:
        stdout = subprocess.check_output(args)
        if useJson:
            return json.loads(stdout)
        else:
            return stdout
    except subprocess.CalledProcessError as e:
        print(e, file=sys.stderr)
        sys.exit(1)


def create_notification(notification_name, notification_email_addr):
    print('Creating notification')
    result_json = run_mon_cli(['notification-create', notification_name,
                         'EMAIL', notification_email_addr])

    # Parse out id
    notification_method_id = result_json['id']
    return notification_method_id


def find_id_for_name(object_json, name):
    for obj in object_json:
        this_name = obj['name']
        if name == this_name:
            return obj['id']
    return None


def cleanup(notification_name, alarm_name):
    # Delete our alarm if it already exists
    alarm_json = run_mon_cli(['alarm-list'])
    alarm_id = find_id_for_name(alarm_json, alarm_name)
    if alarm_id:
        run_mon_cli(['alarm-delete', alarm_id], useJson=False)
    # Delete our notification if it already exists
    notification_json = run_mon_cli(['notification-list'])
    notification_id = find_id_for_name(notification_json, notification_name)
    if notification_id:
        run_mon_cli(['notification-delete', notification_id], useJson=False)


def wait_for_alarm_state_change(alarm_id, old_state):
    # Wait for it to change state
    print('Waiting for alarm to change state from %s' % old_state)
    for x in range(0, 250):
        time.sleep(1)
        state = get_alarm_state(alarm_id)
        if state != old_state:
            print('Alarm state changed to %s in %d seconds' % (state, x))
            return state
    print('State never changed from %s in %d seconds' % (old_state, x),
          file=sys.stderr)
    sys.exit(1)


def main():
    notification_name = 'Jahmon Smoke Test'
    notification_email_addr = 'root@kafka'
    alarm_name = 'high cpu and load'
    metric_name = 'cpu_system_perc'
    metric_dimensions = {'hostname': 'thresh'}
    cleanup(notification_name, alarm_name)

    # Query how many metrics there are for the Alarm
    metric_json = get_metrics(metric_name, metric_dimensions)
    if len(metric_json) == 0:
        print('No measurements received for metric %s ' %
              (metric_name + str(metric_dimensions)), file=sys.stderr)
        return 1

    start_time = time.time()

    initial_num_metrics = len(metric_json[0]['measurements'])

    # Create Notification through CLI
    notification_method_id = create_notification(notification_name,
                                                 notification_email_addr)
    # Create Alarm through CLI
    expression = 'max(cpu_system_perc) > 1 and ' + \
                 'max(load_avg_1_min{hostname=thresh}) > 1'
    description = 'System CPU Utilization exceeds 1% and ' + \
                  'Load exceeds 3 per measurement period'
    alarm_id = create_alarm(alarm_name, expression, notification_method_id,
                            description)
    state = get_alarm_state(alarm_id)
    # Ensure it is created in the right state
    if state != 'UNDETERMINED':
        print('Wrong initial alarm state, expected UNDETERMINED but is %s' %
              state)
        return 1

    state = wait_for_alarm_state_change(alarm_id, 'UNDETERMINED')

    if state != 'ALARM':
        print('Wrong final state, expected ALARM but was %s' % state,
              file=sys.stderr)
        return 1

    state_changes = ['UNDETERMINED', 'ALARM']
    new_state = 'OK'
    state_changes.append(new_state)
    change_alarm_state(alarm_id, new_state)
    # There is a bug in the API which allows this to work. Soon that
    # will be fixed and this will fail
    if len(sys.argv) > 1:
        final_state = 'ALARM'
        state_changes.append(final_state)

        state = wait_for_alarm_state_change(alarm_id, new_state)

        if state != final_state:
            print('Wrong final state, expected %s but was %s' %
                  (final_state, state), file=sys.stderr)
            return 1

    # If the alarm changes state too fast, then there isn't time for the new
    # metric to arrive. Unlikely, but it has been seen
    change_time = time.time() - start_time
    if change_time < 30:
        time.sleep(30 - change_time)
        change_time = 30
    metric_json = get_metrics(metric_name, metric_dimensions)
    final_num_metrics = len(metric_json[0]['measurements'])
    if final_num_metrics <= initial_num_metrics:
        print('No new metrics received', file=sys.stderr)
        return 1
    print('Received %d metrics in %d seconds' %
          ((final_num_metrics - initial_num_metrics),  change_time))
    if not check_alarm_history(alarm_id, state_changes):
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
