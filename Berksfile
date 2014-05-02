require 'rubygems'

if Gem::Specification::find_by_name('berkshelf').version.to_s[0] == '3'
  source 'https://api.berkshelf.com'
end

metadata
cookbook 'mon_api', git: 'git@git.hpcloud.net:mon/cookbooks-mon_api'
cookbook 'kafka', git: 'git@git.hpcloud.net:mon/cookbooks-kafka'
cookbook 'mon_agent', git: 'git@git.hpcloud.net:mon/cookbooks-mon_agent'
cookbook 'mon_notification', git: 'git@git.hpcloud.net:mon/cookbooks-mon_notification'
cookbook 'mon_persister', git: 'git@git.hpcloud.net:mon/cookbooks-mon_persister'
cookbook 'mon_thresh', git: 'git@git.hpcloud.net:mon/cookbooks-mon_thresh'
cookbook 'percona', git: 'https://github.com/tkuhlman/chef-percona', branch: "feature/mini-mon"
cookbook 'vertica', git: 'git@git.hpcloud.net:mon/cookbooks-vertica'
cookbook 'zookeeper', git: 'git@git.hpcloud.net:mon/cookbooks-zookeeper'

# community cookbook we pin
cookbook 'hostsfile', '= 1.0.1'
cookbook 'build-essential', '= 1.4.4'
