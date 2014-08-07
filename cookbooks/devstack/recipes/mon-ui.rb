# Installs the mon-ui panel

# Grab the necessary packages
include_recipe "python"
['monasca-ui','python-monascaclient'].each do |pkg|
    python_pip pkg do
        action :install
    end
end

# Set up symlinks
# Use 'execute' resource because chef does not support symlinking directories
if !::File.exists?("/opt/stack/horizon/monitoring")
    execute "ln -sfv /usr/local/share/monasca/ui/enabled/* /opt/stack/horizon/openstack_dashboard/local/enabled/"
    execute "ln -sv /usr/local/lib/python2.7/dist-packages/monitoring /opt/stack/horizon/monitoring"
end
if ::File.exists?("/usr/local/share/monasca/ui/local_settings.py") && 
   ::File.readlines("/opt/stack/horizon/openstack_dashboard/local/local_settings.py").grep(/MONITORING_SERVICES/).size == 0
    execute "cat /usr/local/share/monasca/ui/local_settings.py >> /opt/stack/horizon/openstack_dashboard/local/local_settings.py"
end

# install grafana and integrate with horizon
if !::File.exists?("/usr/local/lib/python2.7/dist-packages/monitoring/static/grafana")
    execute "git clone https://github.com/hpcloud-mon/grafana.git /opt/stack/grafana"
    execute "cp /opt/stack/grafana/src/config.sample.js /opt/stack/grafana/src/config.js"
    execute "ln -sv /opt/stack/grafana/src /usr/local/lib/python2.7/dist-packages/monitoring/static/grafana"
end

# Bounce the webserver
service "apache2" do
    action :restart
end

