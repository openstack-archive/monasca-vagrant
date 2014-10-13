# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2" # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!

unless Vagrant.has_plugin?("vagrant-berkshelf")
  raise "The needed plugin vagrant-berkshelf is not available.
         Install it by calling 'vagrant plugin install vagrant-berkshelf'."
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  # Settings for all vms
  config.berkshelf.enabled = true

  if Vagrant.has_plugin?("vagrant-cachier")
    config.cache.scope = :box
  end

  # Handle local proxy settings
  if Vagrant.has_plugin?("vagrant-proxyconf")
    if ENV["http_proxy"]
      config.proxy.http = ENV["http_proxy"]
    end
    if ENV["https_proxy"]
      config.proxy.https = ENV["https_proxy"]
    end
    if ENV["no_proxy"]
      config.proxy.no_proxy = ENV["no_proxy"]
    end
  end

  config.vm.synced_folder "~/", "/vagrant_home"

  # One vm just for devstack (to access the UI)
  config.vm.define "devstack" do |ds|
    ds.vm.hostname = "devstack"
    ds.vm.box = "monasca/devstack"
    ds.vm.network :private_network, ip: "192.168.10.5"
    ds.vm.network :private_network, ip: "10.1.2.44"
    ds.vm.provider "virtualbox" do |vb|
      vb.memory = 7168
      vb.cpus = 4
    end
    ds.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Devstack"
      chef.arguments = '--force-formatter'
    end
  end

  # One vm running all the services
  config.vm.define "mini-mon" do |mm|
    mm.vm.hostname = 'mini-mon'
    mm.vm.box = "kuhlmant/precise64_chef11"
    mm.vm.network :private_network, ip: "192.168.10.4"
    mm.vm.provider "virtualbox" do |vb|
      vb.memory = 6144
      vb.cpus = 4
    end
    mm.vm.provision :chef_solo do |chef|
      chef.roles_path = "roles"
      chef.data_bags_path = "data_bags"
      chef.add_role "Mini-Mon"
    end
    mm.vm.provision "ansible" do |ansible|
      ansible.playbook = "mini-mon.yml"
    end
  end

end
