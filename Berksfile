require 'rubygems'

if Gem::Specification::find_by_name('berkshelf').version.to_s[0] == '3'
  source 'https://api.berkshelf.com'
end

cookbook 'mini-mon', path: './cookbooks/mini-mon'
cookbook 'devstack', path: './cookbooks/devstack'
cookbook 'ds-build', path: './cookbooks/ds-build'
cookbook 'mon_api', git: 'https://github.com/stackforge/cookbook-monasca-api'
cookbook 'kafka', git: 'https://github.com/hpcloud-mon/cookbooks-kafka'
cookbook 'monasca_agent', git: 'https://github.com/stackforge/cookbook-monasca-agent'
cookbook 'monasca_notification', git: 'https://github.com/stackforge/cookbook-monasca-notification'
cookbook 'mon_persister', git: 'https://github.com/stackforge/cookbook-monasca-persister.git'
cookbook 'monasca_schema', git: 'https://github.com/hpcloud-mon/cookbook-monasca-schema'
cookbook 'mon_thresh', git: 'https://github.com/hpcloud-mon/cookbooks-mon_thresh'
cookbook 'storm', git: 'https://github.com/tkuhlman/storm'
cookbook 'vertica', git: 'https://github.com/hpcloud-mon/cookbooks-vertica'
cookbook 'zookeeper', git: 'https://github.com/hpcloud-mon/cookbooks-zookeeper'

# Community cookbooks
cookbook 'influxdb', git: 'https://github.com/SimpleFinance/chef-influxdb'
cookbook 'percona', git: 'https://github.com/phlipper/chef-percona'
