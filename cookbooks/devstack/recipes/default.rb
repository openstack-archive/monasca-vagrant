# Modify devstack image (https://vagrantcloud.com/monasca/devstack) as needed
# for use in mini-mon

my_ip = '192.168.10.5'
ks_conf = '/etc/keystone/keystone.conf'

# Modify keystone configuration to use the IP address specified above
execute "sed -i.bak 's^\\(.*endpoint = http://\\).*\\(:.*\\)^\\1#{my_ip}\\2^' #{ks_conf}"

# Reload the apache configuration following this change
service "apache2" do
    action :restart
end

