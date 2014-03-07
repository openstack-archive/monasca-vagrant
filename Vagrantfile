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
  config.vm.define "api" do |api|
    api.vm.hostname = 'api'
    api.vm.network :private_network, ip: "192.168.10.4"
    api.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Api"
    end
  end

  config.vm.define "kafka" do |kafka|
    kafka.vm.hostname = 'kafka'
    kafka.vm.network :private_network, ip: "192.168.10.10"
    kafka.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Kafka"
    end
  end

  config.vm.define "mysql" do |mysql|
    mysql.vm.hostname = 'mysql'
    mysql.vm.network :private_network, ip: "192.168.10.6"
    mysql.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "MySQL"
    end
  end

  config.vm.define "persister" do |persister|
    persister.vm.hostname = 'persister'
    persister.vm.network :private_network, ip: "192.168.10.12"
    persister.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Persister"
    end
  end

  config.vm.define "vertica" do |vertica|
    vertica.vm.hostname = 'vertica'
    vertica.vm.network :private_network, ip: "192.168.10.8"
    vertica.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Vertica"
    end
    vertica.vm.provider "virtualbox" do |vb|
      vb.memory = 2048  # Vertica is pretty strict about its minimum
    end
  end

end
