<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Installation](#installation)
  - [Get the Code](#get-the-code)
  - [Install Vagrant](#install-vagrant)
    - [Install VirtualBox and Vagrant](#install-virtualbox-and-vagrant)
      - [MacOS](#macos)
      - [Linux (Ubuntu)](#linux-ubuntu)
    - [Set Up Berkshelf](#set-up-berkshelf)
      - [MacOS](#macos-1)
      - [Linux (Ubuntu)](#linux-ubuntu-1)
- [Using mini-mon](#using-mini-mon)
  - [Starting mini-mon](#starting-mini-mon)
  - [Mini-mon access information](#mini-mon-access-information)
    - [Internal Endpoints](#internal-endpoints)
  - [Updating](#updating)
  - [Improving Provisioning Speed](#improving-provisioning-speed)
    - [Local cache](#local-cache)
      - [Linux (Ubuntu)](#linux-ubuntu-2)
      - [MacOS](#macos-2)
    - [vagrant-cachier](#vagrant-cachier)
  - [Cookbook Development](#cookbook-development)
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
The following steps assume you have [Homebrew](http://brew.sh/) installed.  Otherwise, install [VirtualBox](http://www.virtualbox.org) and [Vagrant](http://www.vagrantup.com) manually from their websites, then continue with Set Up Berkshelf below.

```
brew tap phinze/cask
brew install brew-cask
brew cask install virtualbox 
brew cask install vagrant
```

#### Linux (Ubuntu)
```
# You need the ruby (>1.9), ruby-dev and build-essential packages installed for these commands to complete

# Specifically for Ubuntu 12.04, you may need to install ruby 1.9 first
sudo apt-get install ruby1.9.3
sudo update-alternatives --set ruby /usr/bin/ruby1.9.1

sudo apt-get install virtualbox
#Download and install latest vagrant from http://www.vagrantup.com/downloads.html
```

### Set Up Berkshelf
#### MacOS
```
vagrant plugin install vagrant-berkshelf --plugin-version '= 2.0.1'
gem install berkshelf
```
#### Linux (Ubuntu)
```
sudo vagrant plugin install vagrant-berkshelf --plugin-version '= 2.0.1'
sudo gem install berkshelf
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
When someone updates the config, this process should allow you to bring up an updated VM.

- `git pull`
- `berks update`
- `vagrant box update`
- `vagrant destroy <vm>` Where `<vm>` is the name of the VM being updated, for example 'vertica'
- `vagrant up`

## Improving Provisioning Speed

The slowest part of the provisioning process is the downloading of deb packages.

### Local cache

To speed this up a local apt-cacher-ng can be used.

#### Linux (Ubuntu)
```
sudo apt-get install apt-cacher-ng
```
#### MacOS
```
brew install apt-cacher-ng
```
Run `apt-cacher-ng -c /usr/local/etc/apt-cacher-ng/` or optionally follow the instructions from brew to start up the cache automatically.
That is all that is needed.  From now on, the cache will be used.

A report from the cache is found at http://localhost:3142/acng-report.html

### vagrant-cachier

Instead of using apt-cacher-ng you can also use the Vagrant plugin
`vagrant-cachier` available at https://github.com/fgrehm/vagrant-cachier. To
use it with this Vagrant box you simply have to install the plugin.

```
sudo vagrant plugin install vagrant-cachier
```

## Cookbook Development

To develop cookbook changes with Vagrant:

- Edit Berksfile, changing the appropriate cookbook line to a local path.  For example:
```
cookbook 'zookeeper', path: '/Users/kuhlmant/src/mon/cookbooks/zookeeper'
```
- Edit your local cookbook as needed
- Run `berks update <cookbook_name>`
- If the Vagrant VM is already up, run `vagrant provision`.  Otherwise, run `vagrant up`
- When finish testing commit and upload your cookbook as normal but don't forget to bump the cookbook version in the metadata.rb.

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
