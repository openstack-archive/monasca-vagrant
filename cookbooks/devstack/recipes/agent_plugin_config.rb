plugin_config = data_bag_item('devstack', 'agent_plugin_config')

service "rabbitmq-server" do
  action :nothing
  supports :status => true, :start => true, :stop => true, :restart => true
end

execute "enable-rabbitmq-web-mgmt" do
    command "/usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management"
    not_if "/usr/lib/rabbitmq/bin/rabbitmq-plugins list -e | grep rabbitmq_management"
    not_if { ::File.file?('/root/.rabbitmq.cnf') }
    notifies :restart, "service[rabbitmq-server]", :delayed
end

template "/root/.rabbitmq.cnf" do
  action :create
  source "rabbitmq.cnf.erb"
  owner 'root'
  group 'root'
  mode 0600
  not_if { ::File.file?('/root/.rabbitmq.cnf') }
  variables(
    :plugin_config => plugin_config
  )
end

include_recipe "mini-mon::mysql_client"
template "/root/.my.cnf" do
  action :create
  source "my.cnf.erb"
  owner 'root'
  group 'root'
  mode 0600
  not_if { ::File.directory?('/root/.my.cnf') }
  variables(
    :plugin_config => plugin_config
  )
end
