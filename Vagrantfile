# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2" # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Settings for all vms
  config.berkshelf.enabled = true

  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.synced_folder "~/", "/vagrant_home"

  # One vm running all the services
  config.vm.hostname = 'mini-mon'
  config.vm.network :private_network, ip: "192.168.10.4"
  config.vm.provider "virtualbox" do |vb|
    vb.memory = 6144
    vb.cpus = 4
  end
  config.vm.provision :chef_solo do |chef|
    chef.roles_path = "roles"
    chef.data_bags_path = "data_bags"
    chef.add_role "Mini-Mon"
  end

end
