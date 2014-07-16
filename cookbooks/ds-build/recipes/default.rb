# Create a devstack image (https://vagrantcloud.com/monasca/devstack)
# from the latest devstack source

# Install git
package 'git' do
    action :install
end

# Remove apt proxy (populated by default in ubuntu/trusty64)
file "/etc/apt/apt.conf.d/01proxy" do
    action :delete
end

# Load up devstack configuration and installer script
cookbook_file "local.conf" do
    mode 0755
    owner "vagrant"
    path "/home/vagrant/local.conf"
    action :create_if_missing
end
cookbook_file "autostack.sh" do
    mode 0755
    owner "vagrant"
    path "/home/vagrant/autostack.sh"
    action :create_if_missing
end

# Install devstack if it hasn't been installed yet
if !::File.exists?("/home/vagrant/devstack/stack-screenrc")
    log "Please wait while devstack is installed.  This WILL take a while." do
        level :info
    end

    execute "/home/vagrant/autostack.sh vagrant"
end


