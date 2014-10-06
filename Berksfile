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
cookbook 'monasca_persister', git: 'https://github.com/stackforge/cookbook-monasca-persister.git'
cookbook 'monasca_schema', git: 'https://github.com/stackforge/cookbook-monasca-schema.git'
cookbook 'monasca_thresh', git: 'https://github.com/stackforge/cookbook-monasca-thresh.git'
cookbook 'storm', git: 'https://github.com/tkuhlman/storm'
cookbook 'zookeeper', git: 'https://github.com/hpcloud-mon/cookbooks-zookeeper'

# Community cookbooks
cookbook 'apt', '= 2.4.0' 
cookbook 'influxdb', git: 'https://github.com/SimpleFinance/chef-influxdb', tag: "2.1.1"
cookbook 'percona', git: 'https://github.com/phlipper/chef-percona', tag: "0.15.5"
