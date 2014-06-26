# Installs the mon-ui panel

# Grab the necessary packages
include_recipe "python"
['monitoring-plugin','python-monclient'].each do |pkg|
    python_pip pkg do
        action :install
    end
end

# Set up symlinks
# Use 'execute' resource because chef does not support symlinking directories
execute "ln -sfv /usr/local/lib/python2.7/dist-packages/enabled/* /opt/stack/horizon/openstack_dashboard/local/enabled/"
execute "ln -sv /usr/local/lib/python2.7/dist-packages/monitoring /opt/stack/horizon/monitoring"
execute "ln -sv /usr/local/lib/python2.7/dist-packages/cosmos/overcloud  /opt/stack/horizon/openstack_dashboard/dashboards/overcloud"

# Bounce the webserver
service "apache2" do
    action :restart
end

