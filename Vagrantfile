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

      # default Ansible selections
      ansible.extra_vars = {
        database_type: "influxdb",
        monasca_persister_java: true,
        monasca_api_java: true
      }

      if ENV["USE_PYTHON_PERSISTER"]
        ansible.extra_vars[:monasca_persister_java] = false
      end

      if ENV["USE_PYTHON_API"]
        ansible.extra_vars[:monasca_api_java] = false
      end

      if ENV["USE_VERTICA"]
        ansible.extra_vars[:database_type] = "vertica"

      elsif ENV["USE_CASSANDRA"]

        # The Monasca API java app checks for existence of influxDB or
        # vertica and dies with an exception if neither is found. The
        # ansible monasca-api role waits for port 8070 (default) to ensure
        # monasca-api is running, which will fail if cassandra has been
        # selected as the database (neither influxDB nor vertica installed)

        # Temporary solution: if Cassandra is selected, install influxdb
        # and cassandra so the Monasca API java app will execute.

        # TODO: determine and implement optimal solution for this conflict

        # ansible.extra_vars[:database_type] = "influxdb"
        # ansible.extra_vars[:database_type2] = "cassandra"
        ansible.extra_vars[:database_type] = "cassandra"
        ansible.extra_vars[:monasca_persister_java] = false
        ansible.extra_vars[:monasca_api_java] = false
      end
    end
  end

end
