from __future__ import print_function

"""
    Utility methods for notifications
"""


def create(mon_client, name, email):
    kwargs = {'name': name, 'address': email, 'type': 'EMAIL'}
    result = mon_client.notifications.create(**kwargs)
    return result['id']


def update(mon_client, notification_id, name, email):
    kwargs = {'id': notification_id, 'name': name, 'address': email,
              'type': 'EMAIL'}
    result = mon_client.notifications.update(**kwargs)
    return result['id']


def get(mon_client, notification_id):
    kwargs = {'notification_id': notification_id}
    result = mon_client.notifications.get(**kwargs)
    return result


def find_by_name(mon_client, name):
    result = mon_client.notifications.list(**{})
    for notification in result:
        if notification['name'] == name:
            return notification
    return None
