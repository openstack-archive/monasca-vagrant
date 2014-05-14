#!/usr/bin/env python
#
"""Notification Engine Test
    Cycle the state of an Alarm the given number of times
"""
from __future__ import print_function
import sys
import time
from monclient import client
from notification import find_notifications
import monclient.exc as exc


def call_mon_api(method, fields):

    try:
        resp = method(**fields)
    except exc.HTTPException as he:
        print(he.code)
        print(he.message)
        sys.exit(1)
    else:
        return resp


def find_alarm_id(mon_client):
    result = call_mon_api(mon_client.alarms.list, {})
    if len(result) == 0:
        print('No existing alarms, create one and rerun test', file=sys.stderr)
        return None
    return result[0]['id']


def get_alarm_state(mon_client, alarm_id):
    result = call_mon_api(mon_client.alarms.get, {'alarm_id': alarm_id})
    return result['state']


def main():
    if len(sys.argv) == 1:
        print('usage: %s count [alarm-id]' % sys.argv[0], file=sys.stderr)
        return 1

    api_version = '2_0'
    endpoint = 'http://192.168.10.4:8080/v2.0'
    kwargs = {'token': '82510970543135'}
    global mon_client
    mon_client = client.Client(api_version, endpoint, **kwargs)

    num_cycles = int(sys.argv[1])
    if len(sys.argv) > 2:
        alarm_id = sys.argv[2]
    else:
        alarm_id = find_alarm_id(mon_client)
        if alarm_id is None:
            return 1

    start_time = time.time()
    initial_state = get_alarm_state(mon_client, alarm_id)
    state = initial_state
    fields = {'alarm_id': alarm_id}

    existing_notifications = find_notifications(alarm_id)
    notifications_sent = num_cycles * 2
    for _ in range(0, notifications_sent):
        if state == 'OK':
            state = 'ALARM'
        else:
            state = 'OK'
        fields['state'] = state
        call_mon_api(mon_client.alarms.patch, fields)
        new_state = get_alarm_state(mon_client, alarm_id)
        if new_state != state:
            print('Expected new state %s but found %s' %
                  (state, new_state), file=sys.stderr)
            return 1
        # time.sleep(1)

    print("Took %d seconds to send %d alarm state changes" %
          ((time.time() - start_time), num_cycles * 2))

    for i in range(0, 30):
        notifications = find_notifications(alarm_id)
        notifications_found = len(notifications) - len(existing_notifications)
        if notifications_found >= notifications_sent:
            break
        print('Found %d of %d expected notifications so far' %
              (notifications_found, notifications_sent))
        time.sleep(1)

    if notifications_found < notifications_sent:
        print('Expected %d notifications but found %d' %
              (notifications_sent, notifications_found), file=sys.stderr)
        return 1

    print('Took %d seconds for notifications to fully arrive' % i)
    result = 0
    return result


if __name__ == "__main__":
    sys.exit(main())
