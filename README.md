<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Installation](#installation)
  - [Get the Code](#get-the-code)
  - [Install Vagrant](#install-vagrant)
    - [Install VirtualBox and Vagrant](#install-virtualbox-and-vagrant)
      - [MacOS](#macos)
      - [Linux (Ubuntu)](#linux-ubuntu)
- [Using mini-mon](#using-mini-mon)
  - [Starting mini-mon](#starting-mini-mon)
  - [Mini-mon access information](#mini-mon-access-information)
    - [Internal Endpoints](#internal-endpoints)
  - [Updating](#updating)
  - [Improving Provisioning Speed](#improving-provisioning-speed)
  - [Ansible Development](#ansible-development)
  - [Running behind a Web Proxy](#running-behind-a-web-proxy)
- [Alternate Vagrant Configurations](#alternate-vagrant-configurations)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Installs a mini monitoring environment based on Vagrant. Intended for development of the monitoring infrastructure.

# Installation

## Get the Code

```
git clone https://github.com/stackforge/monasca-vagrant
```
## Install Vagrant

### Install VirtualBox and Vagrant
Note: Vagrant version 1.5.0 or higher is required.

#### MacOS
The following steps assume you have [Homebrew](http://brew.sh/) installed.  Otherwise, install [VirtualBox](http://www.virtualbox.org) and [Vagrant](http://www.vagrantup.com) and [Ansible](http://www.ansible.com) as suggested on their websites.

```
brew tap phinze/cask
brew install brew-cask
brew cask install virtualbox 
brew cask install vagrant
brew install ansible  # Version 1.8+ is required
ansible-galaxy install -r requirements.yml -p ./roles
```

#### Linux (Ubuntu)
```
sudo apt-get install virtualbox
#Download and install latest vagrant from http://www.vagrantup.com/downloads.html
sudo pip install ansible  # Version 1.8+ is required
ansible-galaxy install -r requirements.yml -p ./roles
```

# Using Monasca Vagrant
## Starting mini-mon
- After installing to start just run `vagrant up`. The first run will download required vagrant boxes.
- When done you can run `vagrant halt` to stop the boxes and later run `vagrant up` to turn them back on. To destroy
  and rebuild run `vagrant destroy -f`. It is typically fastest to use halt/up than to rebuild your vm.
- Run `vagrant help` for more info on standard vagrant commands.

## Basic Monasca usage
The full Monasca stack is running on the mini-mon vm and many devstack services on the devstack vm. A monasca-agent is installed
on both and metrics are actively being collected.
- You can access the horizon UI by navigating to http://192.168.10.5 and logging in as mini-mon/password. This 
  is the UI used for devstack and it contains the Monasca plugin found at the Monitoring tab as well as Grafana used for graphing metrics.
- Run `vagrant ssh <host>` to log in, where `<host>` is either `mini-mon` or `devstack`
- The monasca cli is installed within both vms and the necessary environment variables loaded into the shell. This is a good way to
  explore the metrics in the system. For example to list all metrics, run `monasca metric-list`

## Smoke test
A smoke test exists in the test directory that exercises every major piece of Monasca and culminates with an email sent by
the notification engine. From within the mini-mon vm this directory is exposed as /vagrant/tests and
so `/vagrant/tests/smoke.py` can be run when in a mini-mon terminal. If this test exits correctly the system is working!


## Updating
When someone updates the config, this process should allow you update the VMs, though not every step is needed at all times.

- `git pull`
- `ansible-galaxy install -r requirements.yml -p ./roles -f`
- `vagrant box update` Only needed rarely
- `vagrant provision`, if the vms where halted run `vagrant up` first.
  - It is also possible to Ansible directly to update just parts of the system. See [Ansible Development](#ansible-development) for more info.

## Running behind a Web Proxy
If you are behind a proxy you can install the `vagrant-proxyconf` plugin to have Vagrant honor standard proxy-related environment variables and set the
VM to use them also. It is important that 192.168.10.4, 192.168.10.5, 127.0.0.1 and localhost be in your no_proxy environment variable.
```
vagrant plugin install vagrant-proxyconf
```

# Advanced Usage
## Access information
- Your host OS home dir is synced to `/vagrant_home` on the VM.
- The root dir of the monasca-vagrant repo on your host OS is synced to `/vagrant` on the VM.
- mini-mon is at 192.168.10.4 and devstack is at 192.168.10.5

### Internal Endpoints
- Influxdb web ui is available at http://192.168.10.4:8083 with root/root as user/password
- The Monasca-api is available at http://192.168.10.4:8080
  - The keystone credentials used are mini-mon/password in the mini-mon project. The keystone services on 192.168.10.5 on standard ports.

## Improving Provisioning Speed

The slowest part of the provisioning process is the downloading of packages.
The Vagrant plugin `vagrant-cachier` available at https://github.com/fgrehm/vagrant-cachier
should help by caching repeated dependencies. To use with Vagrant simply install the plugin.

```
sudo vagrant plugin install vagrant-cachier
```

# Monasca Debugging
See this page for details on the [Monasca Architecture](https://wiki.openstack.org/wiki/Monasca).

The components of the system which are part of the Monasca code base have there configuration in `/etc/monasca` and their logs
in `/var/log/monasca`. For nearly all of these you can set the logging to higher debug level and restart. The components of the
system which are dependencies for Monasca (zookeeper, kafka, storm, influxdb, mysql) are either in the standard Ubuntu location
or in `/opt`.

Some other helpful commands:
- Zookeeper shell at - `/usr/share/zookeeper/bin/zkCli.sh`
- Kafka debug commands are at `/opt/kafka/bin` in particular the `kafka-console-consumer.sh` is helpful.
- Running `monasca-collector info` will give an report on the current state of agent checks.
- The storm admin webui exists at `http://192.168.10.4:8088`
- The mysql admin is root/password so you can access the db with the command `mysql -uroot -ppassword mon`

## Ansible Development

### Running Ansible directly

At any point you can rerun `vagrant provision` to rerun the Ansible provisioning. Often it is
easier to run ansible directly and specify tags, ie `ansible-playbook mini-mon.yml --tags api,persister`.
Also a very simple playbook is available for running the smoke test, `ansible-playbook ./smoke.yml`

For these to work smoothly add these vagrant specific settings to
your local ansible configuration (~/.ansible.cfg or a personal ansible.cfg in this dir):

    [defaults]
    hostfile = .ansible_hosts
    remote_user = vagrant
    host_key_checking = False
    # Note: For newer versions of Ansible a single insecure_private_key isn't used, rather it is machine specific
    # by modifying .ansible_hosts adding ansible_ssh_key_file to the end of the line you can configure the proper behavior.
    # In that case leave out the private_key_file line below.
    # For example `devstack ansible_ssh_host=192.168.10.5 ansible_ssh_private_key_file=.vagrant/machines/devstack/virtualbox/private_key`
    private_key_file = ~/.vagrant.d/insecure_private_key

    # In some configurations this won't work, use only if your config permits.
    #[ssh_connection]
    #pipelining = True  # Speeds up connections but only if requiretty is not enabled for sudo

### Editing Ansible Configuration
Since there are only two VMs in this setup the Ansible configuration has no host or group variables, rather
all variables are in the playbook. There is one playbook for each machine, `mini-mon.yml` and `devstack.yml`.
The playbooks contain all variables, some tasks and the roles used in building the VMs.

To edit the Ansible roles I suggest downloading the full git source of the role and putting it in
your ansible path. This allows you to run your changes directly from the git copy you are working on.
See the [Ansible docs](http://docs.ansible.com) for more details on the exact configuration needed.

# Alternate Vagrant Configurations
To run any of these alternate configs, simply run the Vagrant commands from within the subdir.

- `ds-build` subdir - This is used for building a new devstack server image.  It does not typically need to be run.

Previously in the split directory an alternative setup was available with each service split into different vms and using
Vertica rather than influxdb. This was removed simply because it was not being actively maintained as changes occurred. It is still possible
to split up the services and to use Vertica, these are done in test environments and production deployments, however is beyond
the scope of this development environment. Additionaly other alternative setups including running mini-mon in HP Public Cloud
and scripts for putting it on baremetal are also no longer supported.
