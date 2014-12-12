#!/usr/bin/env python

DOCUMENTATION = '''
---
module: monasca_notification_method
short_description: crud operations for Monasca notifications methods
description:
    - Performs crud operations (create/update/delete) on monasca notification methods
    - Monasca project homepage - https://wiki.openstack.org/wiki/Monasca
    - When relevant the notification_id is in the output and can be used with the register action
author: Tim Kuhlman <tim@backgroundprocess.com>
requirements: [ python-monascaclient ]
options:
    address:
        required: true
        description:
            - The notification method address corresponding to the type.
    api_version:
        required: false
        default: '2_0'
        description:
            - The monasca api version.
    keystone_password:
        required: false
        description:
            - Keystone password to use for authentication, required unless a keystone_token is specified.
    keystone_url:
        required: false
        description:
            - Keystone url to authenticate against, required unless keystone_token isdefined.
              Example http://192.168.10.5:5000/v3
    keystone_token:
        required: false
        description:
            - Keystone token to use with the monasca api. If this is specified the monasca_api_url is required but
              the keystone_user and keystone_password aren't.
    keystone_user:
        required: false
        description:
            - Keystone user to log in as, required unless a keystone_token is specified.
    monasca_api_url:
        required: false
        description:
            - If unset the service endpoing registered with keystone will be used.
    name:
        required: true
        description:
            - The notification method name
    state:
        required: false
        default: "present"
        choices: [ present, absent ]
        description:
            - Whether the account should exist.  When C(absent), removes the user account.
    type:
        required: true
        description:
            - The notification type. This must be one of the types supported by the Monasca API.
'''

EXAMPLES = '''
- name: Setup root email notification method
  monasca_notification_method:
    name: "Email Root"
    type: 'EMAIL'
    address: 'root@localhost'
    keystone_url: "{{keystone_url}}"
    keystone_user: "{{keystone_user}}"
    keystone_password: "{{keystone_password}}"
  register: out
- name: Create System Alarm Definitions
  monasca_alarm_definition:
    name: "Host Alive Alarm"
    expression: "host_alive_status > 0"
    keystone_token: "{{out.keystone_token}}"
    monasca_api_url: "{{out.monasca_api_url}}"
    alarm_actions:
      - "{{out.notification_method_id}}"
    ok_actions:
      - "{{out.notification_method_id}}"
    undetermined_actions:
      - "{{out.notification_method_id}}"
'''

from ansible.module_utils.basic import *

try:
    from monascaclient import client
    from monascaclient import ksclient
except ImportError:
    monascaclient_found = False
else:
    monascaclient_found = True


# With Ansible modules including other files presents difficulties otherwise this would be in its own module
class MonascaAnsible(object):
    """ A base class used to build Monasca Client based Ansible Modules
        As input an ansible.module_utils.basic.AnsibleModule object is expected. It should have at least
        these params defined:
        - api_version
        - keystone_token and monasca_api_url or keystone_url, keystone_user and keystone_password and optionally
          monasca_api_url
    """
    def __init__(self, module):
        self.module = module
        self._keystone_auth()
        self.exit_data = {'keystone_token': self.token, 'monasca_api_url': self.api_url}
        self.monasca = client.Client(self.module.params['api_version'], self.api_url, token=self.token)

    def _exit_json(self, **kwargs):
        """ Exit with supplied kwargs combined with the self.exit_data
        """
        kwargs.update(self.exit_data)
        self.module.exit_json(**kwargs)

    def _keystone_auth(self):
        """ Authenticate to Keystone and set self.token and self.api_url
        """
        if self.module.params['keystone_token'] is None:
            ks = ksclient.KSClient(auth_url=self.module.params['keystone_url'],
                                   username=self.module.params['keystone_user'],
                                   password=self.module.params['keystone_password'])

            self.token = ks.token
            if self.module.params['monasca_api_url'] is None:
                self.api_url = ks.monasca_url
            else:
                self.api_url = self.module.params['monasca_api_url']
        else:
            if self.module.params['monasca_api_url'] is None:
                self.module.fail_json(msg='Error: When specifying keystone_token, monasca_api_url is required')
            self.token = self.module.params['keystone_token']
            self.api_url = self.module.params['monasca_api_url']


class MonascaNotification(MonascaAnsible):
    def run(self):
        name = self.module.params['name']
        type = self.module.params['type']
        address = self.module.params['address']

        notifications = {notif['name']:notif for notif in self.monasca.notifications.list()}
        if name in notifications.keys():
            notification = notifications[name]
        else:
            notification = None

        if self.module.params['state'] == 'absent':
            if notification is None:
                self._exit_json(changed=False)
            else:
                self.monasca.notifications.delete(notification_id=notification['id'])
                self._exit_json(changed=True)
        else:  # Only other option is present
            if notification is None:
                body = self.monasca.notifications.create(name=name, type=type, address=address)
                self._exit_json(changed=True, notification_method_id=body['id'])
            else:
                if notification['type'] == type and notification['address'] == address:
                    self._exit_json(changed=False, notification_method_id=notification['id'])
                else:
                    self.monasca.notifications.update(notification_id=notification['id'],
                                                      name=name, type=type, address=address)
                    self._exit_json(changed=True, notification_method_id=notification['id'])


def main():
    module = AnsibleModule(
        argument_spec=dict(
            address=dict(required=True, type='str'),
            api_version=dict(required=False, default='2_0', type='str'),
            keystone_password=dict(required=False, type='str'),
            keystone_token=dict(required=False, type='str'),
            keystone_url=dict(required=False, type='str'),
            keystone_user=dict(required=False, type='str'),
            monasca_api_url=dict(required=False, type='str'),
            name=dict(required=True, type='str'),
            state=dict(default='present', choices=['present', 'absent'], type='str'),
            type=dict(required=True, type='str')
        ),
        supports_check_mode=True
    )

    if not monascaclient_found:
        module.fail_json(msg="python-monascaclient >= 1.0.9 is required")

    notification = MonascaNotification(module)
    notification.run()


if __name__ == "__main__":
    main()
