#!/usr/bin/env bash
# Bootstrap chef-solo on Ubuntu 12.04
                                                                                                                                                             
# Use the local apt mirrors, much faster
sed -i -e 's,^archive.ubuntu.com/ubuntu,nova.clouds.archive.ubuntu.com/ubuntu,g' /etc/apt/sources.list
apt-get -y update
                                                                                                                                                             
# The omnibus installer
if ! [ -e /usr/bin/chef-solo ]; then
  curl -L https://www.opscode.com/chef/install.sh | bash
fi
                                                                                                                                                             
# An alternative to omnibus is to install ruby via apt and then the chef gem
#apt-get -y install ruby1.9.3                                                                                                                                
#gem install --no-ri --no-rdoc chef 
