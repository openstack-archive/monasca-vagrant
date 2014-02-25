# Common setup for all vagrant boxes


## Todo - This apt setup is specific to HP Cloud and should be moved to an optional recipe.

# This move the default apt sources which are the standard ubuntu apt ones aside, so we are forced to deal with what hpcloud has mirrored
bash 'move dist sources.list' do
  action :run
  code 'mv /etc/apt/sources.list /etc/apt/sources.list-dist'
  not_if do ::File.exists?('/etc/apt/sources.list-dist') end
end

apt_repository 'foundation' do
  uri 'http://packages.dev.uswest.hpcloud.net/cloud/foundation'
  arch 'amd64'
  distribution node['lsb']['codename']
  components ['main', 'restricted', 'universe', 'multiverse']
  key 'http://packages.dev.uswest.hpcloud.net/cloud/som/developer/hpcs.gpg'
end

apt_repository 'foundation-updates' do
  uri 'http://packages.dev.uswest.hpcloud.net/cloud/foundation'
  arch 'amd64'
  distribution "#{node['lsb']['codename']}-updates/snapshots/rc20140129"
  components ['main', 'restricted', 'universe', 'multiverse']
  key 'http://packages.dev.uswest.hpcloud.net/cloud/som/developer/hpcs.gpg'
end

apt_repository 'dev' do
  uri 'http://packages.dev.uswest.hpcloud.net/cloud/som/developer'
  arch 'amd64'
  distribution node['lsb']['codename']
  components ['release']
  key 'http://packages.dev.uswest.hpcloud.net/cloud/som/developer/hpcs.gpg'
end
