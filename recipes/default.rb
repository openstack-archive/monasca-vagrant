# Common setup for all vagrant boxes

# Look for a local apt cache, the base repo must be there before the apt cache but it should ideally be before the others
rb = ruby_block "Check for local apt cache" do
  action :nothing
  block do
    if system("wget -T 1 -t 1 http://#{node[:network][:default_gateway]}:#{node[:apt][:cacher_port]}/acng-report.html -O /dev/null > /dev/null 2>&1")
      node.default[:apt][:cacher_ipaddress] = node[:network][:default_gateway]
      node.default[:apt][:cacher_interface] = 'eth0'
      Chef::Log.info('Enabling local apt-cache-ng')
    else
      node.default[:apt][:cacher_ipaddress] = nil
      Chef::Log.info('Disabling local apt-cache-ng')
    end
  end
end

rb.run_action(:create)  # Run during compile time so that apt::cacher-client has the correct variables set

# Add in the cacher-client, it will do something or nothing depending on the value of node[:apt][:cacher_ipaddress]
include_recipe('apt::cacher-client')

apt_repository 'dev' do
  uri 'https://region-a.geo-1.objects.hpcloudsvc.com/v1/46995959297574/mini-mon/public_repo'
  arch 'amd64'
  distribution 'precise'
  components ['release']
  key 'https://region-a.geo-1.objects.hpcloudsvc.com/v1/46995959297574/mini-mon/public_repo/mon.gpg'
end

# The precise image does not have easy_install which is needed by some cookbooks

package 'python-setuptools' do
  action :install
end
