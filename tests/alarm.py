from __future__ import print_function
import sys
#
"""
    Utility methods for CRUD of alarms
"""


def get_state(mon_client, alarm_id):
    result = get(mon_client, alarm_id)
    return result['state']


def get(mon_client, alarm_id):
    result = mon_client.alarms.get(**{'alarm_id': alarm_id})
    return result


def disable(mon_client, alarm_id):
    patch(mon_client, alarm_id, {'actions_enabled': False})


def enable(mon_client, alarm_id):
    patch(mon_client, alarm_id, {'actions_enabled': True})


def set_state(mon_client, alarm_id, state):
    patch(mon_client, alarm_id, {'state': state})
    new_state = get_state(mon_client, alarm_id)
    if new_state != state:
        print('Expected new state %s but found %s' %
              (state, new_state), file=sys.stderr)
        return False
    return True


def patch(mon_client, alarm_id, fields):
    fields['alarm_id'] = alarm_id
    mon_client.alarms.patch(**fields)


def set_optional_field(name, value, fields):
    if value is not None:
        fields[name] = value


def create(mon_client, name, description, expression, ok_actions=None,
           alarm_actions=None, undetermined_actions=None):
    fields = {}
    fields['name'] = name
    fields['expression'] = expression
    set_optional_field('description', description, fields)
    set_optional_field('ok_actions', ok_actions, fields)
    set_optional_field('alarm_actions', alarm_actions, fields)
    set_optional_field('undetermined_actions', undetermined_actions, fields)
    result = mon_client.alarms.create(**fields)
    return result['id']


def find_alarm_byname(mon_client, alarm_name):
    alarms = mon_client.alarms.list(**{})
    for alarm in alarms:
        if alarm['name'] == alarm_name:
            return alarm
    return None
