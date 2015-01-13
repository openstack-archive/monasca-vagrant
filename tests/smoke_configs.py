"""configurations for smoke test"""

import subprocess

system_vars = {
    'default': {}  # the default configuration, assumes monasca-vagrant setup
}


test_config = {
    'default': {}  # the default configuration,
                   # simple test of each component of monasca-vagrant
}


# definition of default system variables
system_vars['default'] = {
    'expected_processes': ('monasca-persister', 'monasca-notification',
                           'kafka', 'zookeeper.jar', 'monasca-api',
                           'influxdb', 'apache-storm', 'mysqld'),
    'mail_host': 'localhost',
    'metric_host': subprocess.check_output(['hostname', '-f']).strip()}


# definition of default test configuration

test_config['default']['system_vars'] = system_vars['default']

test_config['default']['notification'] = {
    'name': 'Monasca Smoke Test',
    'email_addr': 'root@'+test_config['default']['system_vars']['mail_host']}

test_config['default']['alarm'] = {
    'name': 'high cpu and load',
    'expression': 'max(cpu.system_perc) > 0 and ' +
                  'max(load.avg_1_min{hostname=' +
                  test_config['default']['system_vars']['metric_host'] +
                  '}) > 0',
    'description': 'System CPU Utilization exceeds 1% and ' +
                   'Load exceeds 3 per measurement period'}

test_config['default']['metric'] = {
    'name': 'load.avg_1_min',
    'dimensions': {'hostname':
                   test_config['default']['system_vars']['metric_host']}}
