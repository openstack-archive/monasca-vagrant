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
        OS_PROJECT_NAME
        OS_AUTH_URL

    TODO:
        1. Add more logic to give ideas of why a particular step failed, for
           example, alarm did not get created because metrics weren't being
           received
"""

from __future__ import print_function
import argparse
import sys
import os
import time
import cli_wrapper
import utils
import datetime
import psutil
import smoke_configs

config = smoke_configs.test_config["default"]


# parse command line arguments
def parse_commandline_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config', nargs='?', default='default',
                        help='select configuration <CONFIG>')
    return parser.parse_args()


def set_config(config_name):
    global config
    try:
        config = smoke_configs.test_config[config_name]
        print('Using {} Configuration'.format(config_name))
        return True
    except KeyError:
        print('Could not find config "{}"'.format(config_name), file=sys.stderr)
        return False


def get_metrics(name, dimensions, since):
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
    print('Waiting for alarm to change state from {}'.format(old_state))
    for x in range(0, 250):
        time.sleep(1)
        state = cli_wrapper.get_alarm_state(alarm_id)
        if state != old_state:
            print('Alarm state changed to {} in {} seconds'.format(state, x))
            return state
    print('State never changed from {} in {} seconds'.format(old_state, x),
          file=sys.stderr)
    return None


def check_notifications(alarm_id, state_changes):
    print("Checking Notification Engine")
    if not os.path.isfile('/etc/monasca/notification.yaml'):
        print('Notification Engine not installed on this VM,' +
              ' skipping Notifications test',
              file=sys.stderr)
        return False

    notifications = utils.find_notifications(alarm_id, "root")
    if len(notifications) != len(state_changes):
        print('Expected {} notifications but only found {}'.format(
              len(state_changes), len(notifications)), file=sys.stderr)
        return False

    index = 0
    for expected in state_changes:
        actual = notifications[index]
        if actual != expected:
            print('Expected {} but found {} for state change {}'.format(
                  expected, actual, index+1), file=sys.stderr)
            return False
        index = index + 1
    print('Received email notifications as expected')

    return True


def count_metrics(metric_name, metric_dimensions, since):
    # Query how many metrics there are for the Alarm
    metric_json = get_metrics(metric_name, metric_dimensions, since)
    if len(metric_json) == 0:
        print('No measurements received for metric {}{} '.format(
              metric_name, metric_dimensions), file=sys.stderr)
        return None

    return len(metric_json[0]['measurements'])


def ensure_at_least(actual, desired):
    if actual < desired:
        time.sleep(desired - actual)


def wait_for_alarm_creation(alarm_def_id):
    print('Waiting for alarm to be created for Alarm Definition {}'.format(alarm_def_id))
    for x in range(0, 30):
        time.sleep(1)
        alarms = cli_wrapper.find_alarms_for_definition(alarm_def_id)
        if len(alarms) == 1:
            print('Alarm was created in {} seconds'.format(x))
            return alarms[0]
        elif len(alarms) > 1:
            print('{} Alarms were created. Only expected 1'.format(len(alarms)),
                  file=sys.stderr)
            return None

    print('Alarm was not created for Alarm Definition {} in {} seconds'.format(
          alarm_def_id, x), file=sys.stderr)
    return None


def smoke_test():
    notification_name = config['notification']['name']
    notification_addr = config['notification']['addr']
    notification_type = config['notification']['type']
    alarm_definition_name = config['alarm']['name']
    metric_name = config['metric']['name']
    metric_dimensions = config['metric']['dimensions']
    statsd_metric_name = config['statsd_metric']['name']
    statsd_metric_dimensions = config['statsd_metric']['dimensions']

    cleanup(notification_name, alarm_definition_name)

    # Query how many metrics there are for the Alarm
    hour_ago = datetime.datetime.now() - datetime.timedelta(hours=1)
    hour_ago_str = hour_ago.strftime('%Y-%m-%dT%H:%M:%S')
    print('Getting metrics for {}{} '.format(metric_name, metric_dimensions))
    initial_num_metrics = count_metrics(metric_name, metric_dimensions,
                                        hour_ago_str)

    if initial_num_metrics is None or initial_num_metrics == 0:
        msg = ('No metric {} with dimensions {} received in last hour'.format(
               metric_name, metric_dimensions))
        return False, msg

    print('Getting metrics for {}{} '.format(statsd_metric_name, statsd_metric_dimensions))
    initial_statsd_num_metrics = count_metrics(statsd_metric_name, statsd_metric_dimensions, hour_ago_str)

    # statsd metrics may not have been sent yet, which will return None from the CLI wrapper
    if initial_statsd_num_metrics is None:
        initial_statsd_num_metrics = 0

    start_time = time.time()

    # Create Notification through CLI
    notif_id = cli_wrapper.create_notification(notification_name,
                                               notification_addr,
                                               notification_type)

    # Create Alarm through CLI
    expression = config['alarm']['expression']
    description = config['alarm']['description']
    alarm_def_id = cli_wrapper.create_alarm_definition(
        alarm_definition_name,
        expression,
        description=description,
        ok_notif_id=notif_id,
        alarm_notif_id=notif_id,
        undetermined_notif_id=notif_id)

    # Wait for an alarm to be created
    alarm_id = wait_for_alarm_creation(alarm_def_id)

    if alarm_id is None:
        received_num_metrics = count_metrics(metric_name, metric_dimensions,
                                             hour_ago_str)
        if received_num_metrics == initial_num_metrics:
            print('Did not receive any {}{} metrics while waiting'.format(metric_name,metric_dimensions))
        else:
            delta = received_num_metrics - initial_num_metrics
            print('Received {} {} metrics while waiting'.format(delta, metric_name))
        return False, 'Alarm creation error'

    # Ensure it is created in the right state
    initial_state = 'UNDETERMINED'
    if not utils.check_alarm_state(alarm_id, initial_state):
        msg = 'Alarm is in an invalid initial state'
        return False, msg
    states = []
    states.append(initial_state)
    state = wait_for_alarm_state_change(alarm_id, initial_state)
    if state is None:
        msg = 'Alarm is in an invalid state'
        return False, msg

    if state != 'ALARM':
        print('Wrong final state, expected ALARM but was {}'.format(state),
              file=sys.stderr)
        msg = 'Alarm is in an invalid final state'
        return False, msg
    states.append(state)

    new_state = 'OK'
    states.append(new_state)
    if not cli_wrapper.change_alarm_state(alarm_id, new_state):
        msg = 'Unable to change Alarm state'
        return False, msg

    # There is a bug in the API which allows this to work. Soon that
    # will be fixed and this will fail
    if len(sys.argv) > 1:
        final_state = 'ALARM'
        states.append(final_state)

        state = wait_for_alarm_state_change(alarm_id, new_state)
        if state is None:
            msg = 'Alarm is in an unknown state'
            return False, msg

        if state != final_state:
            msg = ('Wrong final state, expected {} but was {}'.format(final_state, state))
            return False, msg

    # If the alarm changes state too fast, then there isn't time for the new
    # metric to arrive. Unlikely, but it has been seen
    ensure_at_least(time.time() - start_time, 35)
    change_time = time.time() - start_time

    final_num_metrics = count_metrics(metric_name, metric_dimensions,
                                      hour_ago_str)
    if final_num_metrics <= initial_num_metrics:
        msg = ('No new metrics received for {}{} in {} seconds'.format(metric_name, metric_dimensions, change_time))
        return False, msg
    print('Received {} metrics in {} seconds'.format((final_num_metrics - initial_num_metrics),  change_time))
    if not utils.check_alarm_history(alarm_id, states):
        msg = 'Invalid alarm history'
        return False, msg

    # Notifications are only sent out for the changes, so omit the first state
    if not check_notifications(alarm_id, states[1:]):
        msg = 'Could not find correct notifications for alarm {}'.format(alarm_id)
        return False, msg

    # Check that monasca statsd is sending metrics
    # Metrics may take some time to arrive
    print('Waiting for statsd metrics')
    for x in range(0,30):
        final_statsd_num_metrics = count_metrics(statsd_metric_name, statsd_metric_dimensions, hour_ago_str)
        if final_statsd_num_metrics > initial_statsd_num_metrics:
            break
        if x >= 29:
            msg = 'No metrics received for statsd metric {}{} in {} seconds'.format(
                  statsd_metric_name, statsd_metric_dimensions, x)
            return False, msg
        time.sleep(1)
    print('Received {0} metrics for {1}{2} in {3} seconds'.format(
        final_statsd_num_metrics-initial_statsd_num_metrics, statsd_metric_name, statsd_metric_dimensions, x))

    msg = ''
    return True, msg


def find_processes():
    """Find_process is meant to validate that all the required processes
    are running before starting the smoke test """
    process_missing = []
    process_list = config['system_vars']['expected_processes']

    for process in process_list:
        process_found_flag = False

        for item in psutil.process_iter():
            for cmd in item.cmdline():
                if process in cmd:
                    process_found_flag = True
                    break

        if not process_found_flag:
            process_missing.append(process)

    if len(process_missing) > 0:   # if processes were not found
        print ('Process = {} Not Found'.format(process_missing))
        return False
    else:
        print ('All Mini-Mon Processes Found')
        return True


def main():
    # May be able to delete this test because the find_process check should
    # validate the notification engine present.
    if not utils.ensure_has_notification_engine():
        return 1

    utils.setup_cli()

    # parse the command line arguments
    cmd_args = parse_commandline_args()

    if not set_config(cmd_args.config):
        return 1

    print('*****VERIFYING HOST ENVIRONMENT*****')
    if find_processes():
        print('*****BEGIN TEST*****')
        complete, msg = smoke_test()
        if not complete:
            print('*****TEST FAILED*****', file=sys.stderr)
            print(msg, file=sys.stderr)
            return 1
    else:
        return 1

    cleanup(config['notification']['name'], config['alarm']['name'])
    print('*****TEST COMPLETE*****')
    return 0


if __name__ == "__main__":
    sys.exit(main())
