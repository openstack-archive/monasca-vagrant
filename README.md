Install as mini monitoring environment based on vagrant, intended for development and monitoring of the monitoring infrastructure.

# Usage
## Setup Vagrant
Assumes you have home brew installed
Also if you are behind a proxy add 'proxy = http://<proxy>' to your ~/.curlrc and set your HTTP_PROXY env variable

- brew tap phinze/cask
- brew install brew-cask
- brew cask install virtualbox 
- brew cask install vagrant

## Start mini-mon

- vagrant up
  - This will bring the vm up
  - Your home dir is synced to the vm in /vagrant_home
- vagrant ssh
  - This will give you shell on the vm
- Your vm is accessible at the ip 10.10.10.10
