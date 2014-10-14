#!/usr/bin/env python
#
"""Notification Engine Test
    CRUD test
"""
from __future__ import print_function
import sys
import os
import time
import notification
import monascaclient.exc as exc
import alarm
import utils


def cycle_states(mon_client, alarm_id, states):
    print('Cycling alarm states through %s' % (states))
    for state in states:
        alarm.set_state(mon_client, alarm_id, state)


def check_notification(alarm_id, user, expected_state, existing):
    for i in range(0, 20):
        notifications = utils.find_notifications(alarm_id, user)
        if len(notifications) > existing:
            break
        time.sleep(1)

    if len(notifications) <= existing:
        print('Did not receive new notification in %d seconds for user %s' %
              (i+1, user), file=sys.stderr)
        return False

    if (len(notifications) - existing) > 1:
        print('Received %d new notifications instead of 1 for user %s' %
              (len(notifications) - existing, user), file=sys.stderr)
        return False

    new_state = notifications[existing]
    if new_state != expected_state:
        print('Expected state %s for user %s but found state %s' %
              (expected_state, user, new_state), file=sys.stderr)
        return False
    print('Found notification for state %s for user %s in %d seconds' %
          (expected_state, user, i), file=sys.stderr)
    return True


def find_or_create_notification(mon_client, name, email):
    notif = notification.find_by_name(mon_client, name)
    if notif is not None:
        if notif['address'] != email:
            print('Notification named %s exists but address is %s not %s' %
                  (name, notif['address'], email), file=sys.stderr)
            return None
        return notif['id']
    else:
        return notification.create(mon_client, name, email)


def check_notifications(alarm_id, email1, email2, email3, state1, state2,
                        state3, existing):
    if not check_notification(alarm_id, email1, state1, existing):
        return False
    if not check_notification(alarm_id, email2, state2, existing):
        return False
    if not check_notification(alarm_id, email3, state3, existing):
        return False
    return True


def print_actions(mon_client, state, action_ids):
    addresses = []
    for action_id in action_ids:
        action_notification = notification.get(mon_client, action_id)
        addresses.append(action_notification['address'])
    print("Notification for %s state sent to %s" % (state, addresses))


def print_notification_setup(mon_client, alarm_id):
    alarm_data = alarm.get(mon_client, alarm_id)
    print_actions(mon_client, 'ALARM', alarm_data['alarm_actions'])
    print_actions(mon_client, 'OK', alarm_data['ok_actions'])
    print_actions(mon_client, 'UNDETERMINED',
                  alarm_data['undetermined_actions'])


def main():
    if not utils.ensure_has_notification_engine():
        return 1

    # Delete notification for OK.Cycle OK, ALARM, UNDETERMINED
    # Ensure proper notifications got written for ALARM, UNDETERMINED

    states = ['OK', 'ALARM', 'UNDETERMINED']
    mon_client = utils.create_mon_client()

    try:
        # Create 3 notifications with different emails, root, kafka,
        # and monasca-agent
        email1 = "root"
        email2 = "kafka"
        email3 = "monasca-agent"
        notification_id_1 = find_or_create_notification(mon_client, email1,
                                                        email1 + "@localhost")
        notification_id_2 = find_or_create_notification(mon_client, email2,
                                                        email2 + "@localhost")
        notification_id_3 = find_or_create_notification(mon_client, email3,
                                                        email3 + "@localhost")

        # Create an alarm. Cycle OK, ALARM, UNDETERMINED,
        alarm_name = "Test Notifications-" + str(os.getpid())
        expr = 'max(not_real_metric{}) > 10'
        alarm_id = alarm.create(mon_client, alarm_name, None, expr,
                                notification_id_1, notification_id_2,
                                notification_id_3)
        print('Created Alarm %s' % alarm_id)
        print_notification_setup(mon_client, alarm_id)
        print('Test initial cycle of Alarms')
        cycle_states(mon_client, alarm_id, states)

        # Ensure proper notifications got written to each
        if not check_notifications(alarm_id, email1, email2, email3,
                                   states[0], states[1], states[2], 0):
            return 1

        # Disable alarm. Cycle OK, ALARM, UNDETERMINED,
        print('Disable Alarm')
        alarm.disable(mon_client, alarm_id)
        cycle_states(mon_client, alarm_id, states)

        # Ensure no new notifications
        if not check_notifications(alarm_id, email1, email2, email3,
                                   states[0], states[1], states[2], 0):
            return 1

        # Enable alarm. Cycle OK, ALARM, UNDETERMINED
        print('Enable Alarm')
        alarm.enable(mon_client, alarm_id)
        cycle_states(mon_client, alarm_id, states)

        # Ensure proper notifications got written to each
        if not check_notifications(alarm_id, email1, email2, email3,
                                   states[0], states[1], states[2], 1):
            return 1

        # Switch Alarm notifications around. Cycle OK, ALARM, UNDETERMINED,
        print("Switch around Alarm notifications")
        alarm.patch(mon_client, alarm_id,
                    {'ok_actions': [notification_id_2],
                     'alarm_actions': [notification_id_3],
                     'undetermined_actions': [notification_id_1]})
        print_notification_setup(mon_client, alarm_id)
        cycle_states(mon_client, alarm_id, states)

        # Ensure proper notifications got written to each
        if not check_notifications(alarm_id, email2, email3, email1,
                                   states[0], states[1], states[2], 2):
            return 1

        # Switch the email addresses around. Cycle OK, ALARM, UNDETERMINED,
        # Ensure proper notifications got written to each
        return 0
    except exc.HTTPException as he:
        print(he.code)
        print(he.message)
        return 1


if __name__ == "__main__":
    sys.exit(main())
