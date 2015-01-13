"""configurations for smoke test"""

import subprocess

system_vars = {
    'default': {  # the default configuration, assumes monasca-vagrant setup
        'expected_processes': ('monasca-persister', 'monasca-notification',
                           'kafka', 'zookeeper.jar', 'monasca-api',
                           'influxdb', 'apache-storm', 'mysqld'),
        'mail_host': 'localhost',
        'metric_host': subprocess.check_output(['hostname', '-f']).strip()}
}


test_config = {
    'default': {   # the default configuration,
                   # simple test of each component of monasca-vagrant
        'system_vars': system_vars['default'],

        'notification': {
            'name': 'Monasca Smoke Test',
            'email_addr': 'root@'+system_vars['default']['mail_host']},

        'alarm': {
            'name': 'high cpu and load',
            'expression': 'max(cpu.system_perc) > 0 and ' +
                          'max(load.avg_1_min{hostname=' +
                          system_vars['default']['metric_host'] +
                          '}) > 0',
            'description': 'System CPU Utilization exceeds 1% and ' +
                           'Load exceeds 3 per measurement period'},

        'metric': {
            'name': 'load.avg_1_min',
            'dimensions': {'hostname':
                            system_vars['default']['metric_host']}}
    }
}