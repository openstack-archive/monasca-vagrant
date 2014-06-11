#!/usr/bin/env python
#
"""Notification Engine Test
    Cycle the state of an Alarm the given number of times
"""
from __future__ import print_function
import sys
import time
import notification
import alarm
import utils


def main():
    if len(sys.argv) == 1:
        print('usage: %s count [alarm-id]' % sys.argv[0], file=sys.stderr)
        return 1

    if not utils.ensure_has_notification_engine():
        return 1

    mon_client = utils.create_mon_client()
    num_cycles = int(sys.argv[1])

    alarm_name = 'notification_cycleTest'
    alarm_json = alarm.find_alarm_byname(mon_client, alarm_name)
    if alarm_json is not None:
        alarm_id = alarm_json['id']
    else:
        existing = notification.find_by_name(mon_client, alarm_name)
        if existing is not None:
            notification_id = existing['id']
        else:
            notification_id = notification.create(mon_client, alarm_name,
                                                  "root@localhost")
        alarm_id = alarm.create(mon_client, alarm_name, None, 'max(cc) > 100',
                                notification_id, notification_id,
                                notification_id)

    user = 'root'
    start_time = time.time()
    initial_state = alarm.get_state(mon_client, alarm_id)
    state = initial_state

    existing_notifications = utils.find_notifications(alarm_id, user)
    notifications_sent = num_cycles * 2
    for _ in range(0, notifications_sent):
        if state == 'OK':
            state = 'ALARM'
        else:
            state = 'OK'
        if not alarm.set_state(mon_client, alarm_id, state):
            return 1

    print("Took %d seconds to send %d alarm state changes" %
          ((time.time() - start_time), num_cycles * 2))

    for i in range(0, 30):
        notifications = utils.find_notifications(alarm_id, user)
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
