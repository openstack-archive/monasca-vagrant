# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2" # Vagrantfile API/syntax version. Don't touch unless you know what you're doing!

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|

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
    ds.vm.provider "virtualbox" do |vb|
      vb.memory = 7168
      vb.cpus = 4
    end
    ds.vm.provision "ansible" do |ansible|
      ansible.playbook = "devstack.yml"
      ansible.raw_arguments = ['-T 30', '-e pipelining=True']
    end
  end

  # One vm running all the services
  config.vm.define "mini-mon" do |mm|
    mm.vm.hostname = 'mini-mon'
    mm.vm.box = "ubuntu/trusty64"
    mm.vm.network :private_network, ip: "192.168.10.4"
    mm.vm.provider "virtualbox" do |vb|
      vb.memory = 6144
      vb.cpus = 4
    end
    mm.vm.provision "ansible" do |ansible|
      ansible.playbook = "mini-mon.yml"
      ansible.raw_arguments = ['-T 30', '-e pipelining=True']
      if ENV["USE_VERTICA"]
        ansible.extra_vars = { database_type: "vertica"}
      else
        ansible.extra_vars = { database_type: "influxdb"}
      end
    end
  end

end
