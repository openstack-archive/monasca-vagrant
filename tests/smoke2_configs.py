# -*- encoding: utf-8 -*-

"""configurations for smoke2 test"""

test_config = {
    'default': {   # the default configuration,
                   # simple test of each component of monasca-vagrant
        'kafka': {
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
            'sub_alarm_definition', 'sub_alarm_definition_dimension',
            'event_transform'
        ],
    },

    'check': {
        'expected_processes': [
            'apache-storm', 'monasca-api', 'monasca-statsd',
            'monasca-collector', 'monasca-forward',
            'monasca-notification', 'monasca-persister',
            'monasca-statsd', 'monasca-forward', 'monasca-collect'
        ]
    },
    'help': {
        'test': 'wiki link for help with specific process'
    }
}
