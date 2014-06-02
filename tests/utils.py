from __future__ import print_function
import sys
import time
import os
import cli_wrapper
from monclient import client

"""
    Utility methods for testing
"""


def check_alarm_history(alarm_id, states):
    transitions = len(states) - 1
    print('Checking Alarm History')
    # May take some time for Alarm history to flow all the way through
    for _ in range(0, 10):
        result_json = cli_wrapper.run_mon_cli(['alarm-history', alarm_id])
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


def check_alarm_state(alarm_id, expected):
    state = cli_wrapper.get_alarm_state(alarm_id)
    if state != expected:
        print('Wrong initial alarm state, expected %s but is %s' %
              (expected, state))
        return False
    return True


def get_api_host():
    # Determine if we are running on multiple VMs or just the one
    if os.path.isfile('/etc/mon/mon-api-config.yml'):
        return 'localhost'
    else:
        return '192.168.10.4'


def setup_cli():
    api_host = get_api_host()

    # These need to be set because we are invoking the CLI as a process
    os.environ['OS_AUTH_TOKEN'] = '82510970543135'
    os.environ['OS_NO_CLIENT_AUTH'] = '1'
    os.environ['MON_API_URL'] = 'http://' + api_host + ':8080/v2.0/'


def create_mon_client():
    api_host = get_api_host()

    api_version = '2_0'
    endpoint = 'http://' + api_host + ':8080/v2.0'
    kwargs = {'token': '82510970543135'}
    return client.Client(api_version, endpoint, **kwargs)


def ensure_has_notification_engine():
    if not os.path.isfile('/etc/mon/notification.yaml'):
        print('Must be run on a VM with Notification Engine installed',
              file=sys.stderr)
        return False
    return True