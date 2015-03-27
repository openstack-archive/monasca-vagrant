from __future__ import print_function
import cli_wrapper
import os
import re
import subprocess
import sys
import time
from monascaclient import client
from monasca_agent.common.keystone import Keystone

"""
    Utility methods for testing
"""


OS_USERNAME = 'mini-mon'
OS_PASSWORD = 'password'
OS_PROJECT_NAME = 'mini-mon'
OS_AUTH_URL = 'http://192.168.10.5:35357/v3/'


def check_alarm_history(alarm_id, states):
    transitions = len(states) - 1
    print('Checking Alarm History')
    # May take some time for Alarm history to flow all the way through
    for _ in range(0, 20):
        result_json = cli_wrapper.run_mon_cli(['alarm-history', alarm_id])
        if len(result_json) >= transitions:
            break
        time.sleep(4)

    result = True
    if transitions != len(result_json):
        print('Wrong number of history entries, expected %d but was %d' %
              (transitions, len(result_json)), file=sys.stderr)
        return False
    # Alarm history is sorted by date
    index = 0
    for i in range(0, transitions):
        old_state = states[i]
        new_state = states[i+1]
        alarm_json = result_json[index]
        if not check_expected(old_state, alarm_json['old_state'], 'old_state',
                              i):
            result = False
        if not check_expected(new_state, alarm_json['new_state'], 'new_state',
                              i):
            result = False
        if not check_expected(alarm_id, alarm_json['alarm_id'], 'alarm_id',
                              i):
            result = False
        index = index + 1

    if result:
        print('Alarm History is OK')
    return result


def check_expected(expected, actual, what, index):
    if (expected == actual):
        return True
    print('Wrong %s for alarm history expected %s but was %s transition %d' %
          (what, expected, actual, index+1), file=sys.stderr)
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


def set_if_not_env(name, default):
    if name not in os.environ:
        os.environ[name] = default
    elif default != os.environ[name]:
        print('%s already set to %s' % (name, os.environ[name]))


def setup_cli():
    api_host = get_api_host()

    # These need to be set because we are invoking the CLI as a process
    set_if_not_env('OS_USERNAME', OS_USERNAME)
    set_if_not_env('OS_PASSWORD', OS_PASSWORD)
    set_if_not_env('OS_PROJECT_NAME', OS_PROJECT_NAME)
    set_if_not_env('OS_AUTH_URL', OS_AUTH_URL)
    os.environ['http_proxy'] = ''
    os.environ['https_proxy'] = ''
    os.environ['HTTP_PROXY'] = ''
    os.environ['HTTPS_PROXY'] = ''


def create_mon_client():
    api_host = get_api_host()

    token = get_token(OS_USERNAME, OS_PASSWORD, OS_PROJECT_NAME,
                      OS_AUTH_URL)

    api_version = '2_0'
    endpoint = 'http://' + api_host + ':8080/v2.0'
    kwargs = {'token': token}
    return client.Client(api_version, endpoint, **kwargs)


def get_token(os_username, os_password, os_project_name, os_auth_url):
    kwargs = { 'keystone_url': os_auth_url,
               'username': os_username,
               'password': os_password,
              'project_domain_name':os_project_name}
    keystone = Keystone(kwargs)

    return keystone.refresh_token()


def ensure_has_notification_engine():
    if not os.path.isfile('/etc/monasca/notification.yaml'):
        print('Must be run on a VM with Notification Engine installed',
              file=sys.stderr)
        return False
    return True


def find_notifications(alarm_id, user):
    args = ['sudo', 'cat', '/var/mail/' + user]
    result = []
    try:
        stdout = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

    previous = ''
    for line in stdout.splitlines():
        # Get the state; the alarm_id always follows the state message
        if alarm_id in line:
            """ In the notification message the state verb is framed by
            'transitioned to the ' and ' state'
            """
            result.append(re.search('transitioned to the (.+?) state',
                                    previous).group(1))
        previous = line
    return result
