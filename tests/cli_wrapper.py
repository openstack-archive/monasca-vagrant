#!/usr/bin/env python
#
""" Wrapper code for running the CLI as a process.
"""
from __future__ import print_function
import sys
import subprocess
import json


def find_obj_for_name(object_json, name):
    for obj in object_json:
        this_name = obj['name']
        if name == this_name:
            return obj
    return None


def find_alarm_by_name(alarm_name):
    alarm_json = run_mon_cli(['alarm-list'])
    return find_obj_for_name(alarm_json, alarm_name)


def delete_alarm_if_exists(alarm_name):
    alarm_json = find_alarm_by_name(alarm_name)
    if alarm_json:
        run_mon_cli(['alarm-delete', alarm_json['id']], useJson=False)


def delete_notification_if_exists(notification_name):
    notification_json = run_mon_cli(['notification-list'])
    notification = find_obj_for_name(notification_json, notification_name)
    if notification:
        run_mon_cli(['notification-delete', notification['id']], useJson=False)


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
    notification_id = result_json['id']
    return notification_id


def get_alarm_state(alarm_id):
    result_json = run_mon_cli(['alarm-show', alarm_id])
    return result_json['state']


def patch_alarm(alarm_id, what, value):
    result_json = run_mon_cli(['alarm-patch', what, value, alarm_id])
    return result_json


def change_alarm_state(alarm_id, new_state):
    print('Changing Alarm state to %s' % new_state)
    result_json = patch_alarm(alarm_id, '--state', new_state)
    if result_json['state'] != new_state:
        print('Alarm patch failed, expected state of %s but was %s' %
              (result_json['state'], new_state), file=sys.stderr)
        return 1


def create_alarm(name, expression, description=None, ok_notif_id=None,
                 alarm_notif_id=None,
                 undetermined_notif_id=None):
    args = ['alarm-create']
    add_argument_if_given(args, '--description', description)
    add_argument_if_given(args, '--alarm-actions', alarm_notif_id)
    add_argument_if_given(args, '--ok-actions', ok_notif_id)
    add_argument_if_given(args, '--undetermined-actions',
                          undetermined_notif_id)
    args.append(name)
    args.append(expression)
    print('Creating alarm')
    result_json = run_mon_cli(args)

    # Parse out id
    alarm_id = result_json['id']
    return alarm_id


def add_argument_if_given(args, arg, value):
    if value is not None:
        args.append(arg)
        args.append(value)