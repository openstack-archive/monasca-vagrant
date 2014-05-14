#!/usr/bin/env python
#
# Copyright (c) 2014 Hewlett-Packard Development Company, L.P.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.
# See the License for the specific language governing permissions and
# limitations under the License.
""" Fabric Tasks for installing mini-mon on baremetal
These tasks were developed for hLinux but will likely work on any decently up to date debian based distro
"""

from fabric.api import *


@task
def chef_solo(chef_dir='/vagrant', run_list='role[Mini-Mon'):
    """Runs chef-solo
        This assumes chef solo and other dependencies are setup.
    """
    # Setup solo.rb
    solo_content = """
    cookbook_path "{dir}/cookbooks"
    role_path "{dir}/roles"
    data_bag_path "{dir}/data_bags"
    """.format(dir=chef_dir)
    sudo('echo %s > %s/solo.rb' % (solo_content, chef_dir))

    # Setup node.json
    node_json = '{ "run_list": "%s" }' % run_list
    sudo('echo "%s" > %s/node.json' % (node_json, chef_dir))

    # Run chef-solo
    sudo('chef-solo -c {dir}/solo.rb -j {dir}/node.json'.format(dir=chef_dir))


@task(default=True)
def install(install_dir='/vagrant'):  # /vagrant to match assumptions in mini-mon even though vagrant is not used here
    """Installs the latest mini-mon and bits necessary to run chef-solo and runs chef-solo on the box.
    """
    execute(install_deps)

    #Clone mini-mon
    sudo('git clone https://github.com/hpcloud-mon/mon-vagrant.git %s' % install_dir)
    # currently the one-vm setup is on a branch
    with cd(install_dir):
        sudo('git checkout feature/one-vm')

    # download cookbooks
    with cd(install_dir):
        sudo('berks vendor cookbooks')

    # the vertica packages from my.vertica.com are needed, this assumes they are one level up from where this script is
    put('../vertica*.deb', install_dir, use_sudo=True)

    execute(chef_solo)


@task
def install_berkshelf():
    """Installs berkshelf."""
    # todo check for ruby 1.9.2 or greater
    # If needed use rvm to get a newer ruby - curl -sSL https://get.rvm.io | bash -s stable --ruby
    sudo('gem install berkshelf')


@task
def install_chef():
    """Installs chef via omnibus."""
    sudo('apt-get install -y curl')
    sudo('curl -L https://www.opscode.com/chef/install.sh | bash')


@task
def install_deps():
    """Install all dependencies needed for running chef-solo"""
    with settings(hide('running', 'output')):
        sudo('apt-get install -y git')
        execute(install_chef)
        execute(install_berkshelf)
