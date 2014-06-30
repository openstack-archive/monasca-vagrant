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
""" Fabric Tasks for installing a cluster monitoring stack on baremetal
These tasks were developed for hLinux but will likely work on any decently up to date debian based distro
"""
from fabric.api import *
from fabric.tasks import Task
import os

from baremetal import chef_solo, git_mini_mon, install_deps


__all__ = ['setup']


class SetupCluster(Task):

    def __init__(self):
        """Setup a cluster running monitoring.
        """
        self.cluster_dir = '/var/tmp/chef-Mon-Node'
        self.mini_mon_dir = '/vagrant'  # mini_mon_dir is /vagrant to match assumptions in mini-mon

    def run(self):
        """Installs the latest cookbooks and dependencies to run chef-solo and runs chef-solo on each box.
            The data bags in the cluster subdir should be properly setup for the environment before running.
        """
        execute(install_deps)
        execute(git_mini_mon, self.mini_mon_dir)

        execute(prep_chef, self.cluster_dir, self.mini_mon_dir)
        execute(copy_vertica, self.mini_mon_dir)

        execute(chef_solo, self.cluster_dir, "role[Mon-Node]")
        if len(env.hosts) > 1:
            execute(chef_solo, self.cluster_dir, "role[Thresh-Nimbus]", host=env.hosts[0])
            execute(chef_solo, self.cluster_dir, "role[Thresh-Supervisor]", hosts=env.hosts[1:])
        else:
            puts('Only one host specified, the Thresh roles will not be run as they require at least two hosts')
            

@task
def prep_chef(cluster_dir, berks_dir):
    """ Pull down cookbooks with bershelf and put roles/data bags in place.
    """
    # download cookbooks
    with settings(hide('running', 'output', 'warnings'), warn_only=True):
        sudo('rm -r %s' % cluster_dir)
        sudo('mkdir %s' % cluster_dir)

    with cd(berks_dir):
        with settings(hide('running', 'output', 'warnings'), warn_only=True):
            berks_check = sudo('ls Berksfile.lock')

        if berks_check.succeeded:
            sudo('berks update')
        else:
            sudo('berks install')
        sudo('berks vendor %s/berks-cookbooks' % cluster_dir)

    # Copy roles and data bags - assumes you are running from the utils directory
    put('%s/cluster/data_bags' % os.path.dirname(env.real_fabfile), cluster_dir, use_sudo=True)
    put('%s/cluster/roles' % os.path.dirname(env.real_fabfile), cluster_dir, use_sudo=True)

@task
def copy_vertica(dest_dir):
    """Copies vertica debs to the remote box
    """
    vertica_packages = ['vertica_7.0.1-0_amd64.deb', 'vertica-r-lang_7.0.1-0_amd64.deb']

    # the vertica packages from my.vertica.com are needed, this assumes they are one level up from cwd
    for deb in vertica_packages:
        with settings(hide('running', 'output', 'warnings'), warn_only=True):
            if run('ls %s/%s' %(dest_dir, deb)).failed:
                puts('Uploading %s' % deb)
                put('../../vertica*.deb', dest_dir, use_sudo=True)


setup = SetupCluster()
