Install's a mini monitoring environment based on vagrant. Intended for development and monitoring of the monitoring infrastructure.

# Usage

## Get the Code

```
git clone https://git.hpcloud.net/mon/mini-mon.git
```

## Setup Vagrant

### Install Vagrant
Assumes you have home homebrew installed, if not download and install VirtualBox and Vagrant from their websites then continue  with Setup Berkshelf.

```
brew tap phinze/cask
brew install brew-cask
brew cask install virtualbox 
brew cask install vagrant
```

### Setup Berkshelf
```
vagrant plugin install vagrant-berkshelf
gem install berkshelf  or gem install --http-proxy <http://some-proxy.foo.com:8088> berkshelf
```

## Start mini-mon
Berkshelf will download some cookbooks from the community so http_proxy and https_proxy environment variables must be set if applicable.
From within the `mini-mon` directory, to start all the vms run:

```
vagrant up
```

- Your home dir is synced to `/vagrant_home` on each vm
- Vms created
  - `kafka` at `192.168.10.10`
  - `mysql` at `192.168.10.6`
  - `persister` at `192.168.10.12`
  - `vertica` at `192.168.10.8`
- Run `vagrant help` for more info
- Run `vagrant ssh <vm name>` to login to a particular vm
- Can also run `ssh vagrant@<ip address>` to login 
  - password is `vagrant`
  

## Updating a VM
When someone updates the config for a vm this process should allow you to bring up an updated vm.
- `git pull`
- `vagrant destroy vm` - Where vm is the name of the vm being updated, for example 'vertica'
- `berks update`
- `vagrant up vm`
