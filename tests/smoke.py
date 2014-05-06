#!/usr/bin/env python
#
"""smoke
    Runs a smoke test of the jahmon installation on mini-mon by ensuring metrics are flowing and creating a new
    notification, alarm and that the Threshold Engine changes the state of the alarm.
    This requires the mon CLI and must be run on one of the mini-mon VMs. Tested running on kafka VM.
    Get it by following the instructions on https://wiki.hpcloud.net/display/iaas/Monitoring+CLI.
    If you want to see the notification, you must install postfix on the kakfa VM, configure it to be local, and
    modify /etc/mon/notification.yaml to use localhost for the email server, then restart

    TODO:
        1. Add check of alarm history when that works
        2. Add check of notification history when that is implemented
        3. Add check of mail getting to root when postfix is added mini-mon. This script will have to run on the kafka VM
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

os.environ["OS_AUTH_TOKEN"] = "82510970543135"
os.environ["OS_NO_CLIENT_AUTH"] = "1"
os.environ["MON_API_URL"] = "http://192.168.10.4:8080/v2.0/"

def get_alarm_state(alarm_id):
    stdout = run_mon_cli(["mon", "--json", "alarm-show", alarm_id])
    response_json = json.loads(stdout)
    return response_json['state']

def check_alarm_history(alarm_id):
    print('Checking Alarm History')
    # Make take a little bit of time for Alarm history to flow all the way through
    for x in range(0, 10):
        stdout = run_mon_cli(["mon", "--json", "alarm-history", alarm_id])
        response_json = json.loads(stdout)
        if len(response_json) > 0:
            break
        time.sleep(4)

    result = True
    if not check_expected(1, len(response_json), 'number of history entries'):
        return False
    alarm_json = response_json[0]
    if not check_expected('UNDETERMINED', alarm_json['old_state'], 'old_state'):
        result = False
    if not check_expected('ALARM', alarm_json['new_state'], 'new_state'):
        result = False
    if not check_expected(alarm_id, alarm_json['alarm_id'], 'alarm_id'):
        result = False
    if result:
        print("Alarm History is OK")
    return result

def check_expected(expected, actual, what):
    if (expected == actual):
        return True
    print("Incorrect value for alarm history " + what + " expected '" + str(expected) + "' but was '" + str(actual) + "'", file=sys.stderr)
    return False

def create_alarm(name, expression, notification_method_id, description=None):
    args = ["mon", "alarm-create"]
    if (description):
            args.append("--description")
            args.append(description)
    args.append("--alarm-actions")
    args.append(notification_method_id)
    args.append("--ok-actions")
    args.append(notification_method_id)
    args.append("--undetermined-actions")
    args.append(notification_method_id)
    args.append(name)
    args.append(expression)
    print("Creating alarm")
    stdout = run_mon_cli(args)
    response_json = json.loads(stdout)

    # Parse out id
    alarm_id = response_json['id']
    return alarm_id 

def get_metrics(name, dimensions):
    print("Getting metrics for " + name + str(dimensions))
    dimensions_arg = ""
    for key, value in dimensions.iteritems():
        if dimensions_arg != "":
            dimensions_arg = dimensions_arg + ","
        dimensions_arg = dimensions_arg + key + "=" + value
    stdout = run_mon_cli(["mon", "--json", "measurement-list", "--dimensions", dimensions_arg, name, "00"])
    return json.loads(stdout)

def run_mon_cli(args):
    try:
        stdout = subprocess.check_output(args)
        return stdout
    except subprocess.CalledProcessError as e:
        print(e, file=sys.stderr)
        sys.exit(1)

def create_notification(notification_name, notification_email_addr):
    print("Creating notification")
    stdout = run_mon_cli(["mon", "notification-create", notification_name, "EMAIL", notification_email_addr])
    response_json = json.loads(stdout)

    # Parse out id
    notification_method_id = response_json['id']
    return notification_method_id 

def find_id_for_name(object_json, name):
    for obj in object_json:
        this_name = obj['name']
        if name == this_name:
            return obj['id']
    return None

def cleanup(notification_name, alarm_name):
    # Delete our alarm if it already exists
    alarm_json = json.loads(run_mon_cli(["mon", "--json", "alarm-list"]))
    alarm_id = find_id_for_name(alarm_json, alarm_name)
    if alarm_id:
        run_mon_cli(["mon", "alarm-delete", alarm_id])
    # Delete our notification if it already exists
    notification_json = json.loads(run_mon_cli(["mon", "--json", "notification-list"]))
    notification_id = find_id_for_name(notification_json, notification_name)
    if notification_id:
        run_mon_cli(["mon", "notification-delete", notification_id])

def main():
    notification_name = "Jahmon Smoke Test"
    notification_email_addr = "root@kafka"
    alarm_name = "high cpu and load"
    metric_name = "cpu_system_perc"
    metric_dimensions = {"hostname":"thresh"}
    cleanup(notification_name, alarm_name)

    # Query how many metrics there are for the Alarm
    metric_json = get_metrics(metric_name, metric_dimensions)
    if len(metric_json) == 0:
        print("No measurements received for metric " + metric_name + str(metric_dimensions), file=sys.stderr)
        sys.exit(1)

    initial_num_metrics = len(metric_json[0]['measurements'])

    # Create Notification through CLI 
    notification_method_id = create_notification(notification_name, notification_email_addr)
    # Create Alarm through CLI
    alarm_id = create_alarm(alarm_name, "max(cpu_system_perc) > 1 and max(load_avg_1_min{hostname=thresh}) > 3", notification_method_id, "System CPU Utilization exceeds 1% and Load exeeds 3 per measurement period")
    state = get_alarm_state(alarm_id)
    # Ensure it is created in the right state
    if state != 'UNDETERMINED':
        print("Wrong initial alarm state, expected UNDETERMINED but was " + state)
        sys.exit(1)
    # Wait for it to 
    print("Waiting for alarm to change state")
    change_time = 0
    for x in range(0, 250):
        time.sleep(1)
        state = get_alarm_state(alarm_id)
        if state != 'UNDETERMINED':
            print("Alarm state changed in " + str(x) + " seconds")
            change_time = x
            break

    if state != 'ALARM':
        print("Wrong final state, expected ALARM but was " + state, file=sys.stderr)
        sys.exit(1)
    print("Final state of alarm was " + state)
    # If the alarm changes state too fast, then there isn't time for the new metric to arrive.
    # Unlikely, but it has been seen
    if change_time < 30:
        time.sleep(30 - change_time)
        change_time = 30
    metric_json = get_metrics(metric_name, metric_dimensions)
    final_num_metrics = len(metric_json[0]['measurements'])
    if final_num_metrics <= initial_num_metrics:
        print("No new metrics received", file=sys.stderr)
        sys.exit(1)
    print("Received " + str(final_num_metrics - initial_num_metrics) + " metrics in " + str(change_time) + " seconds")
    if not check_alarm_history(alarm_id):
        sys.exit(1)

    return 0
    
    
if __name__ == "__main__":
    sys.exit(main())
