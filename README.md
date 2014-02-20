Install's a mini monitoring environment based on vagrant. Intended for development and monitoring of the monitoring infrastructure.

# Usage

## Get the Code

```
git clone https://git.hpcloud.net/mon/mini-mon.git
```

## Setup Vagrant
Assumes you have home homebrew installed. Also if you are behind a proxy add `proxy = http://<proxy>` to your `~/.curlrc` and set your `HTTP_PROXY` environment variable

```
brew tap phinze/cask
brew install brew-cask
brew cask install virtualbox 
brew cask install vagrant
vagrant plugin install vagrant-berkshelf
gem install berkshelf
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
- Run `vagrant help` for more info
