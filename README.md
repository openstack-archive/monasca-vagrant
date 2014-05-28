<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Installation](#installation)
  - [Get the Code](#get-the-code)
  - [Setup Vagrant](#setup-vagrant)
    - [Install Vagrant](#install-vagrant)
    - [Setup Berkshelf](#setup-berkshelf)
- [Using mini-mon](#using-mini-mon)
  - [Updating](#updating)
  - [Improving Provisioning Speed](#improving-provisioning-speed)
  - [Cookbook Development](#cookbook-development)
- [Alternate Setups](#alternate-setups)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->

Install's a mini monitoring environment based on vagrant. Intended for development and monitoring of the monitoring infrastructure.

# Installation

## Get the Code

```
git clone https://github.com/hpcloud-mon/mon-vagrant
```
Vertica must be downloaded from the [Vertica site](https://my.vertica.com/). Download these packages and place in the root of this repository.
- vertica_7.0.1-0_amd64.deb
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
vagrant plugin install vagrant-berkshelf --plugin-version '>= 2.0.1'
gem install berkshelf
```

# Using mini-mon

- Your home dir is synced to `/vagrant_home` on the vm
- The vm will have an ip of 196.168.10.4 that can be access from other services running on the host.
- Run `vagrant ssh` to login
- Run `vagrant help` for more info

## Updating
When someone updates the config this process should allow you to bring up an updated vm.
- `git pull`
- `berks update`
- `vagrant destroy` - Where vm is the name of the vm being updated, for example 'vertica'
- `vagrant up`

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

# Alternate Vagrant Configurations
To run any of these alternate configs, simply run the Vagrant commands from within the subdir, though note the vertica debs must be copied into
the subdir also.

- A Vagrant config for running the various monitoring components split into their own vms is available in the split subdir.
- A Vagrant config for testing hLinux is available in the hlinux subdir
- Baremetal - actually not using Vagrant at all, see the baremetal fabric task in the utils directory.
