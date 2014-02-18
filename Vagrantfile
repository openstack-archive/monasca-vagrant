# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2" # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Settings for all vms
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  config.vm.synced_folder "~/", "/vagrant_home"
  config.berkshelf.enabled = true

  # VM specific settings
  config.vm.define "kafka" do |kafka|
    kafka.vm.network :private_network, ip: "10.10.10.10"
    kafka.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"

      chef.add_role "Kafka"
    end
  end

end
