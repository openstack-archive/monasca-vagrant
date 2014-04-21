# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2" # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Settings for all vms
  config.berkshelf.enabled = true

  # To enable hLinux reverse the commented lines below and all of the 'chef.synced_folder_type = rsync' lines
  config.vm.box = "precise64"
  config.vm.box_url = "http://files.vagrantup.com/precise64.box"
  #config.vm.box = "hlinux"
  #config.vm.box_url = "http://packages.dev.uswest.hpcloud.net/cloud/som/hlinux.box"
  #config.vm.guest = :debian   # bypass vagrant guest type autodetection
  # hlinux is not currently working with virtual box shared folders so minimize shared folders and switch to rsync
  config.vm.synced_folder "~/", "/vagrant_home"
  #config.vm.synced_folder ".", "/vagrant", disabled: true
  #config.vm.provider "virtualbox" do |vb|
  #  vb.customize ["modifyvm", :id, "--natdnshostresolver1", "on"]
  #  vb.customize ["modifyvm", :id, "--natdnsproxy1", "on"]
  #end

  # VM specific settings, these machines come up in order they are specified.
  config.vm.define "mysql" do |mysql|
    mysql.vm.hostname = 'mysql'
    mysql.vm.network :private_network, ip: "192.168.10.6"
    mysql.vm.provision :chef_solo do |chef|
      #chef.synced_folder_type = "rsync"
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "MySQL"
    end
  end

  config.vm.define "kafka" do |kafka|
    kafka.vm.hostname = 'kafka'
    kafka.vm.network :private_network, ip: "192.168.10.10"
    kafka.vm.provision :chef_solo do |chef|
      #chef.synced_folder_type = "rsync"
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Kafka"
    end
    kafka.vm.provider "virtualbox" do |vb|
      vb.memory = 1024
    end
  end

  config.vm.define "vertica" do |vertica|
    vertica.vm.hostname = 'vertica'
    vertica.vm.network :private_network, ip: "192.168.10.8"
    vertica.vm.provision :chef_solo do |chef|
      #chef.synced_folder_type = "rsync"
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Vertica"
    end
    vertica.vm.provider "virtualbox" do |vb|
      vb.memory = 2048  # Vertica is pretty strict about its minimum
    end
  end

  config.vm.define "api" do |api|
    api.vm.hostname = 'api'
    api.vm.network :private_network, ip: "192.168.10.4"
    api.vm.provision :chef_solo do |chef|
      #chef.synced_folder_type = "rsync"
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Api"
    end
  end

  config.vm.define "persister" do |persister|
    persister.vm.hostname = 'persister'
    persister.vm.network :private_network, ip: "192.168.10.12"
    persister.vm.provision :chef_solo do |chef|
      #chef.synced_folder_type = "rsync"
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Persister"
    end
  end

  config.vm.define "thresh" do |thresh|
    thresh.vm.hostname = 'thresh'
    thresh.vm.network :private_network, ip: "192.168.10.14"
    thresh.vm.provision :chef_solo do |chef|
      #chef.synced_folder_type = "rsync"
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Thresh"
    end
  end

end
