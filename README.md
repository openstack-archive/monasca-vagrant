<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Installation](#installation)
  - [Get the Code](#get-the-code)
  - [Setup Vagrant](#setup-vagrant)
    - [Install Vagrant](#install-vagrant)
    - [Setup Berkshelf](#setup-berkshelf)
- [Using mini-mon](#using-mini-mon)
  - [Start mini-mon](#start-mini-mon)
  - [Halt mini-mon](#halt-mini-mon)
  - [Updating a VM](#updating-a-vm)
  - [Improving Provisioning Speed](#improving-provisioning-speed)
  - [Cookbook Development](#cookbook-development)
- [Running hLinux as the base OS](#running-hlinux-as-the-base-os)
  - [Creating a new hLinux box](#creating-a-new-hlinux-box)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Install's a mini monitoring environment based on vagrant. Intended for development and monitoring of the monitoring infrastructure.

# Installation

## Get the Code

```
git clone https://github.com/hpcloud-mon/mon-vagrant
```
Vertica must be downloaded from the [Vertica site](https://my.vertica.com/). Download these packages and place in the root of this repository.
- vertica_7.0.1-0_amd64.db
- vertica-R-lang_7.0.1_amd64.deb

The vertica::console recipe is not enabled by default but if it is added this package is also needed.
- vertica-console_7.0.1-0_amd64.deb

## Setup Vagrant

### Install Vagrant
Assumes you have home homebrew installed, if not download and install VirtualBox and Vagrant from their websites then continue with Setup Berkshelf.

```
brew tap phinze/cask
brew install brew-cask
brew cask install virtualbox 
brew cask install vagrant
```

### Setup Berkshelf
```
vagrant plugin install vagrant-berkshelf
gem install berkshelf
```

# Using mini-mon

- Your home dir is synced to `/vagrant_home` on each vm
- Vms created
  - `api` at `192.168.10.4`
  - `kafka` at `192.168.10.10` - mon-notification runs on this box also
  - `mysql` at `192.168.10.6`
  - `persister` at `192.168.10.12`
  - `thresh` at `192.168.10.14`
  - `vertica` at `192.168.10.8`
    - The management console is at https://192.168.10.8:5450
- Run `vagrant help` for more info
- Run `vagrant ssh <vm name>` to login to a particular vm
- Can also run `ssh vagrant@<ip address>` to login 
  - password is `vagrant`
  
## Start mini-mon
From within the `mini-mon` directory, to start all the vms run:
```
bin/vup
```
The standard vagrant commands can also be used, the vup script just starts things up in a dependency order using parallel startup.

## Halt mini-mon
In some cases halting mini-mon can result in certain vms being left in an odd state, to avoid this a script has been made to halt boxes in the 
correct order
```
bin/vhalt
```

## Updating a VM
When someone updates the config for a vm this process should allow you to bring up an updated vm.
- `git pull`
- `berks update`
- `vagrant destroy vm` - Where vm is the name of the vm being updated, for example 'vertica'
- `vagrant up vm`

## Improving Provisioning Speed
The slowest part of the provisioning process is the downloading of deb packages. To speed this up a local apt-cacher-ng can be used.
To install on a mac
```
brew install apt-cacher-ng
```
Run `apt-cacher-ng -c /usr/local/etc/apt-cacher-ng/` or optionally follow the instructions from brew to start up the cache automatically.
That is all that is needed from now on the cache will be used.

A report from the cache is found at http://localhost:3142/acng-report.html

## Cookbook Development

To develop cookbook changes with Vagrant:
- Edit Berksfile changing the appropriate cookbook line to a local path, ie `cookbook 'zookeeper', path: '/Users/kuhlmant/src/mon/cookbooks/zookeeper'`
- Edit your local cookbook as needed.
- run 'berks update <cookbook_name>'
- If the vagrant vm is already up run 'vagrant provision' if not run 'Vagrant up'
- When finish testing commit and upload your cookbook as normal but don't forget to bump the cookbook version in the metadata.rb.

# Running hLinux as the base OS
hLinux can be installed and run as the base OS for all the vms defined in mini-mon. To this comment/uncomment the appropriate lines in the Vagrantfile.
Also switch to the proper base apt repos in recipes/default.rb. There are a couple of minor problem which would slow down development and are why at
this point hLinux has not been turned on by default:
- The vboxsf filesystem driver is not working correctly in hLinux, this prevents home directory syncing.
- Slow network performance of the hLinux vbox image makes some tasks annoying.

## Creating a new hLinux box
The [hLinux](http://hlinux-home.usa.hp.com/wiki/index.php/Main_Page) box used in mini-mon is created via [packer](http://www.packer.io/), config is in
the templates directory.

- Install packer
  - `brew tap homebrew/binary`
  - `brew install packer`
- Run packer
  - `cd templates`
  - `packer build hlinux.json`
- From the mini-mon directory run `vagrant box add hlinux templates/packer_virtualbox-iso_virtualbox.box`
  - If you have an existing hLinux box you man need to first remove it `vagrant box remove hlinux`
  - Also upload to a server for others to download.
