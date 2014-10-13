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
brew install ansible
ansible-galaxy install -r ansible_roles
```

#### Linux (Ubuntu)
```
sudo apt-get install virtualbox
#Download and install latest vagrant from http://www.vagrantup.com/downloads.html
sudo pip install ansible
ansible-galaxy install -r ansible_roles
```

# Using mini-mon
## Starting mini-mon
- After installing to start just run `vagrant up`. The first run will download required vagrant boxes.
- Run `vagrant help` for more info on standard vagrant commands.

## Mini-mon access information
- Your host OS home dir is synced to `/vagrant_home` on the VM.
- The root dir of the monasca-vagrant repo on your host OS is synced to `/vagrant` on the VM.
- The main VM will have an IP of 192.168.10.4 that can be access from other services running on the host.
- An additional VM running DevStack will be created at 192.168.10.5
- Run `vagrant ssh <host>` to log in, where `<host>` is either `mini-mon` or `devstack`

### Internal Endpoints
- You can access UI by navigating to http://192.168.10.5 and logging in as mini-mon with password
- Influxdb is available at http://192.168.10.4:8083 with root/root as user/password
- The Monasca-api is available at http://192.168.10.4:8080
- The keystone credentials used are mini-mon/password in the mini-mon project. The keystone services in 192.168.10.5 on standard ports.

## Updating
When someone updates the config, this process should allow you to bring up an updated VM, though not every step is needed at all times.

- `git pull`
- `ansible-galaxy install -r ansible_roles`
- `vagrant box update`
- `vagrant destroy <vm>` Where `<vm>` is the name of the VM being updated, for example 'vertica'
- `vagrant up`

## Improving Provisioning Speed

The slowest part of the provisioning process is the downloading of packages.
The Vagrant plugin `vagrant-cachier` available at https://github.com/fgrehm/vagrant-cachier
should help by caching repeated dependencies. To use with Vagrant simply install the plugin.

```
sudo vagrant plugin install vagrant-cachier
```

## Ansible Development

To edit the Ansible roles I suggest downloading the full git source of the role and putting it in
your ansible path. Then though you can rerun `vagrant provision` to test your changes, often it is
easier to run ansible directly. For this to work smoothly add these vagrant specific settings to
your local ansible configuration
    
    hostfile = .vagrant/provisioners/ansible/inventory/vagrant_ansible_inventory
    private_key_file = ~/.vagrant.d/insecure_private_key
    remote_user = vagrant

## Running behind a Web Proxy
If you are behind a proxy you can install the `vagrant-proxyconf` pluging to have Vagrant honor standard proxy-related environment variables and set the
VM to use them also.
```
vagrant plugin install vagrant-proxyconf
```

# Alternate Vagrant Configurations
To run any of these alternate configs, simply run the Vagrant commands from within the subdir.

- `ds-build` subdir - This is used for building a new devstack server image.  It does not typically need to be run.

Previously in the split directory an alternative setup was available with each service split into different vms and using
Vertica rather than influxdb. This was removed simply because it was not being actively maintained as changes occurred. It is still possible
to split up the services and to use Vertica, these are done in test environments and production deployments, however is beyond
the scope of this development environment. Additionaly other alternative setups including running mini-mon in HP Public Cloud
and scripts for putting it on baremetal are also no longer supported.
