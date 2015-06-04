# -*- encoding: utf-8 -*-

"""configurations for smoke2 test"""

test_config = {
    'default': {   # the default configuration,
                   # simple test of each component of monasca-vagrant
        'kafka': {
            'url': "192.168.10.4:9092",
            'topics': [
                'metrics', 'events', 'raw-events', 'transformed-events',
                'stream-definitions', 'transform-definitions',
                'alarm-state-transitions', 'alarm-notifications',
                'retry-notifications'
            ]
        },
        'mysql_schema': [
            'alarm', 'alarm_action', 'alarm_definition', 'alarm_metric',
            'metric_definition', 'metric_definition_dimensions',
            'metric_dimension', 'notification_method', 'schema_migrations',
            'stream_actions', 'stream_definition', 'sub_alarm',
            'sub_alarm_definition', 'sub_alarm_definition_dimension'
        ],
        'mysql_user': 'monapi',
        'mysql_pass': 'password',
        'influxdb_user': 'mon_api',
        'influxdb_pass': 'password',
        'keystone': {
            'user': 'mini-mon',
            'pass': 'password',
            'auth_url': 'http://192.168.10.5:35357/v3'
        }

    },

    'check': {
        'packages': {
            'apt': [
                'python-dev', 'python-pip',
                'openjdk-7-jre-headless', 'percona-agent',
                'zookeeperd', 'influxdb'
            ],
            'pip': [
                'monasca_agent', 'monasca_notification', 'monascastatsd',
                'python_keystoneclient', 'python_monascaclient'
            ],
            'pip_location': '/opt/monasca/lib/python2.7/site-packages/'
        },
        'expected_processes': [
            'apache-storm', 'monasca-api', 'monasca-agent',
            'monasca-notification', 'monasca-persister',
            'monasca-statsd', 'monasca-forward', 'monasca-collect'
        ]
    },
    'help': {
        'monasca-notification': 'wiki link'
    }
}
