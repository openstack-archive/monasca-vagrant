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
def chef_solo(chef_dir='/vagrant', run_list='role[Mini-Mon]', proxy=None):
    """Runs chef-solo
        This assumes chef solo and other dependencies are setup.
    """
    # Setup solo.rb
    solo_content = '''cookbook_path "{dir}/cookbooks"
role_path "{dir}/roles"
data_bag_path "{dir}/data_bags"'''.format(dir=chef_dir)
    sudo("echo '%s' > %s/solo.rb" % (solo_content, chef_dir))

    # Setup node.json
    node_json = '{ "run_list": "%s" }' % run_list
    sudo("echo '%s' > %s/node.json" % (node_json, chef_dir))

    # Run chef-solo
    # todo - proxy hell defeats chef at this point because some components like pip need it but others like apt choke
    with prefix(proxy_string(proxy)):
        sudo('chef-solo -c {dir}/solo.rb -j {dir}/node.json'.format(dir=chef_dir))


@task(default=True)
def install(install_dir='/vagrant', proxy=None):
    """Installs the latest mini-mon and bits necessary to run chef-solo and runs chef-solo on the box.
        proxy is an optional proxy url used for http and https, it is not used for apt as that is assumed to be
        correctly setup.
        install_dir defaults to /vagrant to match assumptions from mini-mon even though vagrant is not used here
    """
    if proxy is not None:
        abort('Proxy support is incomplete.')
    execute(install_deps, proxy)

    #Clone mini-mon
    with prefix(proxy_string(proxy)):
        # Update the install dir if it already has code, otherwise check out
        with settings(hide('running', 'output', 'warnings'), warn_only=True):
            install_dir_check = run('ls %s' % install_dir)

        if install_dir_check.succeeded:
            with cd(install_dir):
                sudo('git pull -f origin master')
        else:
            sudo('git clone https://github.com/hpcloud-mon/mon-vagrant.git %s' % install_dir)

        # download cookbooks
        with cd(install_dir):
            sudo('berks vendor cookbooks')

        # the vertica packages from my.vertica.com are needed, this assumes they are one level up from cwd
        put('../vertica*.deb', install_dir, use_sudo=True)

        execute(chef_solo, proxy)


@task
def install_berkshelf(proxy=None):
    """Installs berkshelf."""
    # check for ruby 1.9.2 or greater and if needed install
    with settings(hide('running', 'output', 'warnings'), warn_only=True):
        ruby_check = run('ruby -v')
        if ruby_check.failed:
            # Install both ruby and tools needed to build gems
            sudo('apt-get install -y ruby ruby-hitimes build-essential')
        else:
            # A better semantic version check like semantic_version module provides would be nice
            version_parts = ruby_check.split()[1].split('.')
            if int(version_parts[0]) < 2 and int(version_parts[1]) < 9:
                abort('Ruby reports version %s, > 1.9.2 is needed' % ruby_check)

    with prefix(proxy_string(proxy)):
        sudo('gem install berkshelf')


@task
def install_chef(proxy=None):
    """Installs chef via omnibus."""
    sudo('apt-get install -y curl')

    # If chef is already installed continue
    with settings(hide('running', 'output', 'warnings'), warn_only=True):
        chef_check = run('chef-solo -v')
        if chef_check.succeeded:
            return

    # Run the omnibus installer
    with prefix(proxy_string(proxy)):
        sudo('curl -s -S -L https://www.opscode.com/chef/install.sh | bash')


@task
def install_deps(proxy=None):
    """Install all dependencies needed for running chef-solo"""
    sudo('apt-get install -y git')
    execute(install_chef, proxy)
    execute(install_berkshelf, proxy)


def proxy_string(proxy):
    """Return a string using the given proxy url.
       An example proxy to pass in myproxy.me.com:8080
    """
    if proxy is None:
        return "no_proxy="  # I have to return a noop string as the prefix context manager will add it to the cmd
    else:
        return "export http_proxy='http://{proxy}' && export https_proxy='http://{proxy}'".format(proxy=proxy)
