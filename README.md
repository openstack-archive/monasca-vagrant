Install's a mini monitoring environment based on vagrant. Intended for development and monitoring of the monitoring infrastructure.

# Usage

## Get the Code

```
git clone https://git.hpcloud.net/mon/mini-mon.git
```

## Setup Vagrant
Assumes you have home homebrew installed.

```
brew tap phinze/cask
brew install brew-cask
brew cask install virtualbox 
brew cask install vagrant
vagrant plugin install vagrant-berkshelf
gem install berkshelf  or gem install --http-proxy <http://some-proxy.foo.com:8088> berkshelf
```

If you are behind a proxy you can install the `vagrant-proxyconf` pluging to have Vagrant honor any proxy-related
environment variables that are set. Note that this is all or nothing with this set all apt repositories use the proxy.:

```
vagrant plugin install vagrant-proxyconf
```

## Start mini-mon

From within the `mini-mon` directory, run:

```
vagrant up
```

- This will bring the vms up
- Your home dir is synced to the vm in /vagrant_home on each vm
- Vms created
  - `kafka` at `192.168.10.10`
  - `mysql` at `192.168.10.6`
  - `persister` at `192.168.10.12`
  - `vertica` at `192.168.10.8`
- Run `vagrant help` for more info
- Run `vagrant ssh <vm name>` to login to a particular vm
- Can also run `ssh vagrant@<ip address>` to login 
  - password is `vagrant`
  
