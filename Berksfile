require 'rubygems'

if Gem::Specification::find_by_name('berkshelf').version.to_s[0] == '3'
  source 'https://api.berkshelf.com'
end

cookbook 'mini-mon', path: './cookbooks/mini-mon'
cookbook 'devstack', path: './cookbooks/devstack'
cookbook 'ds-build', path: './cookbooks/ds-build'
cookbook 'monasca_api', git: 'https://github.com/stackforge/cookbook-monasca-api'
cookbook 'monasca_agent', git: 'https://github.com/stackforge/cookbook-monasca-agent'
cookbook 'monasca_thresh', git: 'https://github.com/stackforge/cookbook-monasca-thresh.git'
cookbook 'storm', git: 'https://github.com/tkuhlman/storm'

# Community cookbooks
cookbook 'apt', '= 2.4.0' 
