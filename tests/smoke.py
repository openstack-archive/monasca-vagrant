#!/usr/bin/env python
#
"""smoke
    Runs a smoke test of the monitoring installation on mini-mon to ensure
    the components (other than the UI) are functioning. The code tests these
    components:
       1. Agent - ensures metrics are being sent to API
       2. API - ensures alarm definitions can created, listed, etc. Ensure
                metrics and alarms can be queried
       3. CLI - used to talk to the API
       4. Persister - ensures metrics and alarm history has been persisted
                      in database because API can query them
       5. Threshold Engine - ensures alarms are created and change state
       6. Notification Engine - ensures email notifications are sent to the
                                local system
    This must be run on either the mini-mon VM for the single VM mode or
    on the kafka VM in the multi VM mode.

    If the tests are to be run in a different environment other than mini-mon,
    the environment variables below can be set and the smoke will use those
    instead of the mini-mon credentials and settings:

        OS_USERNAME
        OS_PASSWORD
        OS_TENANT_NAME
        OS_AUTH_URL
        MONASCA_API_URL

    TODO:
        1. Add more logic to give ideas of why a particular step failed, for
           example, alarm did not get created because metrics weren't being
           received
"""

from __future__ import print_function
import sys
import os
import subprocess
import time
import cli_wrapper
import utils
import datetime
import psutil

process_list = ('monasca-persister', 'monasca-notification', 'kafka', 'zookeeper.jar',
                'monasca-api', 'influxdb', 'apache-storm', 'mysqld')


def get_metrics(name, dimensions, since):
    print('Getting metrics for %s ' % (name + str(dimensions)))
    dimensions_arg = ''
    for key, value in dimensions.iteritems():
        if dimensions_arg != '':
            dimensions_arg = dimensions_arg + ','
        dimensions_arg = dimensions_arg + key + '=' + value
    return cli_wrapper.run_mon_cli(['measurement-list', '--dimensions',
                                    dimensions_arg, name, since])


def cleanup(notification_name, alarm_definition_name):
    cli_wrapper.delete_alarm_definition_if_exists(alarm_definition_name)
    cli_wrapper.delete_notification_if_exists(notification_name)


def wait_for_alarm_state_change(alarm_id, old_state):
    # Wait for it to change state
    print('Waiting for alarm to change state from %s' % old_state)
    for x in range(0, 250):
        time.sleep(1)
        state = cli_wrapper.get_alarm_state(alarm_id)
        if state != old_state:
            print('Alarm state changed to %s in %d seconds' % (state, x))
            return state
    print('State never changed from %s in %d seconds' % (old_state, x),
          file=sys.stderr)
    return None


def check_notifications(alarm_id, state_changes):
    if not os.path.isfile('/etc/monasca/notification.yaml'):
        print('Notification Engine not installed on this VM,' +
              ' skipping Notifications test',
              file=sys.stderr)
        return False

    notifications = utils.find_notifications(alarm_id,"root")
    if len(notifications) != len(state_changes):
        print('Expected %d notifications but only found %d' %
              (len(state_changes), len(notifications)), file=sys.stderr)
        return False

    index = 0
    for expected in state_changes:
        actual = notifications[index]
        if actual != expected:
            print('Expected %s but found %s for state change %d' %
                  (expected, actual, index+1), file=sys.stderr)
            return False
        index = index + 1
    print('Received email notifications as expected')

    return True


def count_metrics(metric_name, metric_dimensions, since):
    # Query how many metrics there are for the Alarm
    metric_json = get_metrics(metric_name, metric_dimensions, since)
    if len(metric_json) == 0:
        print('No measurements received for metric %s ' %
              (metric_name + str(metric_dimensions)), file=sys.stderr)
        return None

    return len(metric_json[0]['measurements'])


def ensure_at_least(actual, desired):
    if actual < desired:
        time.sleep(desired - actual)


def wait_for_alarm_creation(alarm_definition_id):
    print('Waiting for alarm to be created for Alarm Definition %s' % alarm_definition_id)
    for x in range(0, 30):
        time.sleep(1)
        alarms = cli_wrapper.find_alarms_for_definition(alarm_definition_id)
        if len(alarms) == 1:
            print('Alarm was created in %d seconds' % x)
            return alarms[0]
        elif len(alarms) > 1:
            print('%d Alarms were created. Only expected 1' % len(alarms),
                  file=sys.stderr)
            return None
    print('Alarm was not created for Alarm Definition %s in %d seconds' % (alarm_definition_id, x),
          file=sys.stderr)
    return None


def smoke_test(mail_host, metric_host):
    notification_name = 'Monasca Smoke Test'
    notification_email_addr = 'root@' + mail_host
    alarm_definition_name = 'high cpu and load'
    metric_name = 'cpu.load_avg_1_min'
    metric_dimensions = {'hostname': metric_host}
    cleanup(notification_name, alarm_definition_name)

    # Query how many metrics there are for the Alarm
    hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    hour_ago_str = hour_ago.strftime('%Y-%m-%dT%H:%M:%S')
    initial_num_metrics = count_metrics(metric_name, metric_dimensions,
                                        hour_ago_str)

    if initial_num_metrics is None or initial_num_metrics == 0:
        print('No metric %s with dimensions %s received in last hour' %
              (metric_name, metric_dimensions), file=sys.stderr)
        return False

    start_time = time.time()

    # Create Notification through CLI
    notification_id = cli_wrapper.create_notification(notification_name,
                                                      notification_email_addr)

       # Create Alarm through CLI
    expression = 'max(cpu.system_perc) > 0 and ' + \
                 'max(cpu.load_avg_1_min{hostname=' + metric_host + '}) > 0'
    description = 'System CPU Utilization exceeds 1% and ' + \
                  'Load exceeds 3 per measurement period'
    alarm_definition_id = cli_wrapper.create_alarm_definition(alarm_definition_name, expression,
                                                              description=description,
                                                              ok_notif_id=notification_id,
                                                              alarm_notif_id=notification_id,
                                                              undetermined_notif_id=notification_id)

    # Wait for an alarm to be created
    alarm_id = wait_for_alarm_creation(alarm_definition_id)
    if alarm_id is None:
        return False

    # Ensure it is created in the right state
    initial_state = 'UNDETERMINED'
    if not utils.check_alarm_state(alarm_id, initial_state):
        return False
    states = []
    states.append(initial_state)
    state = wait_for_alarm_state_change(alarm_id, initial_state)
    if state is None:
        return False

    if state != 'ALARM':
        print('Wrong final state, expected ALARM but was %s' % state,
              file=sys.stderr)
        return False
    states.append(state)

    new_state = 'OK'
    states.append(new_state)
    cli_wrapper.change_alarm_state(alarm_id, new_state)
    # There is a bug in the API which allows this to work. Soon that
    # will be fixed and this will fail
    if len(sys.argv) > 1:
        final_state = 'ALARM'
        states.append(final_state)

        state = wait_for_alarm_state_change(alarm_id, new_state)
        if state is None:
            return False

        if state != final_state:
            print('Wrong final state, expected %s but was %s' %
                  (final_state, state), file=sys.stderr)
            return False

    # If the alarm changes state too fast, then there isn't time for the new
    # metric to arrive. Unlikely, but it has been seen
    ensure_at_least(time.time() - start_time, 35)
    change_time = time.time() - start_time

    final_num_metrics = count_metrics(metric_name, metric_dimensions,
                                      hour_ago_str)
    if final_num_metrics <= initial_num_metrics:
        print('No new metrics received in %d seconds' % change_time,
              file=sys.stderr)
        return False
    print('Received %d metrics in %d seconds' %
          ((final_num_metrics - initial_num_metrics),  change_time))
    if not utils.check_alarm_history(alarm_id, states):
        return False

    # Notifications are only sent out for the changes, so omit the first state
    if not check_notifications(alarm_id, states[1:]):
        return False

    return True


def find_processes():
    """Find_process is meant to validate that all the required processes
    are running before starting the smoke test """
    process_missing = []

    for process in process_list:  # process_list is a global defined at top of module
        process_found_flag = False

        for item in psutil.process_iter():
            for cmd in item.cmdline():
                if process in cmd:
                    process_found_flag = True
                    break

        if not process_found_flag:
            process_missing.append(process)

    if len(process_missing) > 0:   # if processes were not found
        print ('Process = %s Not Found' % process_missing)
        return False
    else:
        print ('All Mini-Mon Processes Found')
        return True


def main():
    # May be able to delete this test because the find_process check should validate the notification engine present.
    if not utils.ensure_has_notification_engine():
        return 1

    utils.setup_cli()

    mail_host = 'localhost'
    metric_host = subprocess.check_output(['hostname']).strip()

    if find_processes():
        if not smoke_test(mail_host, metric_host):
            return 1
    else:
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
