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

from baremetal import chef_solo, git_mini_mon, install_deps


__all__ = ['setup']


class SetupCluster(Task):

    def __init__(self):
        """Setup a cluster running monitoring.
        """
        self.cluster_dir = '/var/tmp/chef-Mon-Node'
        self.cluster_hosts = None
        self.mini_mon_dir = '/vagrant'  # mini_mon_dir is /vagrant to match assumptions in mini-mon

    def run(self):
        """Installs the latest cookbooks and dependencies to run chef-solo and runs chef-solo on each box.
            The data bags in the cluster subdir should be properly setup for the environment before running.
        """
        self.cluster_hosts = env.hosts

        execute(install_deps)
        execute(git_mini_mon, self.mini_mon_dir)

        # download cookbooks
        with cd(self.cluster_dir):
            sudo('berks vendor')

        # the vertica packages from my.vertica.com are needed, this assumes they are one level up from cwd
        put('../vertica*.deb', self.mini_mon_dir, use_sudo=True)

        # Copy roles and data bags
        put('%s/utils/cluster/data_bags' % self.mini_mon_dir, self.cluster_dir, use_sudo=True)
        put('%s/utils/cluster/roles' % self.mini_mon_dir, self.cluster_dir, use_sudo=True)

        execute(chef_solo, self.cluster_dir, "role[Mon-Node]")


setup = SetupCluster()
