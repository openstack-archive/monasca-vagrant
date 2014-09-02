plugin_config = data_bag_item('monasca_agent', 'agent_plugin_config')
node_name = Chef::Config[:node_name]
if !File.file?('/root/.rabbitmq.cnf')
  service "rabbitmq-server" do
    action :nothing
    supports :status => true, :start => true, :stop => true, :restart => true
  end
  execute "enable-rabbitmq-web-mgmt" do
      command "/usr/lib/rabbitmq/bin/rabbitmq-plugins enable rabbitmq_management"
      not_if "/usr/lib/rabbitmq/bin/rabbitmq-plugins list -e | grep rabbitmq_management"
      notifies :restart, "service[rabbitmq-server]", :delayed
  end
  template "/root/.rabbitmq.cnf" do
    action :create
    source "rabbitmq.cnf.erb"
    owner 'root'
    group 'root'
    mode 0600
    variables(
      :plugin_config => plugin_config,
      :node_name => node_name
    )
  end
end

if !File.file?('/root/.my.cnf')
  include_recipe "mini-mon::mysql_client"
  template "/root/.my.cnf" do
    action :create
    source "my.cnf.erb"
    owner 'root'
    group 'root'
    mode 0600
    variables(
      :plugin_config => plugin_config,
      :node_name => node_name
    )
  end
end
