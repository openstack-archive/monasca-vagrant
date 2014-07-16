require 'rubygems'

if Gem::Specification::find_by_name('berkshelf').version.to_s[0] == '3'
  source 'https://api.berkshelf.com'
end

cookbook 'mini-mon', path: './cookbooks/mini-mon'
cookbook 'devstack', path: './cookbooks/devstack'
cookbook 'ds-build', path: './cookbooks/ds-build'
cookbook 'mon_api', git: 'https://github.com/hpcloud-mon/cookbooks-mon_api'
cookbook 'kafka', git: 'https://github.com/hpcloud-mon/cookbooks-kafka'
cookbook 'mon_agent', git: 'https://github.com/hpcloud-mon/cookbooks-mon_agent'
cookbook 'mon_notification', git: 'https://github.com/hpcloud-mon/cookbooks-mon_notification'
cookbook 'mon_persister', git: 'https://github.com/hpcloud-mon/cookbooks-mon_persister.git'
cookbook 'mon_thresh', git: 'https://github.com/hpcloud-mon/cookbooks-mon_thresh'
cookbook 'storm', git: 'https://github.com/tkuhlman/storm'
cookbook 'vertica', git: 'https://github.com/hpcloud-mon/cookbooks-vertica'
cookbook 'zookeeper', git: 'https://github.com/hpcloud-mon/cookbooks-zookeeper'

# Community cookbooks
cookbook 'influxdb', git: 'https://github.com/SimpleFinance/chef-influxdb'
cookbook 'percona', git: 'https://github.com/phlipper/chef-percona'
