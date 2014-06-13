# Turn a devstack image (https://vagrantcloud.com/cyrusbio/devstack) into
# something useful to mini-mon

admin_token = 'ADMIN'
my_ip = '192.168.10.5'
ks_conf = '/etc/keystone/keystone.conf'

# Modify keystone configuration to...
## ...bind to all IPs
execute "sed -i.bak1 's^\\(.*bind_host = \\).*^\\10.0.0.0^' #{ks_conf}"
# ...set the default admin token
execute "sed -i.bak2 's^\\(admin_token = \\).*^\\1#{admin_token}^' #{ks_conf}"
# ...set endpoints that other mini-mon nodes can use
execute "sed -i.bak3 's^\\(.*endpoint = http://\\).*\\(:.*\\)^\\1#{my_ip}\\2^' #{ks_conf}"


# Regular devstack relies on a user manually running "rejoin-stack.sh" which
# fires up a bunch of screen sessions, one for each process.  We don't really
# want that here.  Instead autostack.sh will create upstart scripts for each
# devstack process, sendnig its output to real log files under /var/log/. 
cookbook_file "autostack.sh" do
    mode 0755
    owner "vagrant"
    path "/home/vagrant/devstack/autostack.sh"
    action :create_if_missing
end

execute "/home/vagrant/devstack/autostack.sh"


