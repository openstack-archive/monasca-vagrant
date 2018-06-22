**Table of Contents**

-  `Installation`_

   -  `Get the Code`_
   -  `Install Vagrant`_

      -  `Install VirtualBox and Vagrant`_

         -  `MacOS`_
         -  `Linux (Ubuntu)`_

-  `Using Monasca Vagrant`_

   -  `Starting mini-mon`_
   -  `Basic Monasca usage`_
   -  `Smoke test`_
   -  `Updating`_
   -  `Running behind a Web Proxy`_
   -  `Running with Vertica`_

-  `Advanced Usage`_

   -  `Access information`_

      -  `Internal Endpoints`_

   -  `Improving Provisioning Speed`_

-  `Monasca Debugging`_

   -  `Ansible Development`_

      -  `Running Ansible directly`_
      -  `Editing Ansible Configuration`_

-  `Developing Monasca`_
-  `Alternate Vagrant Configurations`_
-  `Troubleshooting`_

Installs a mini monitoring environment based on Vagrant. Intended for
development of the monitoring infrastructure.

Installation
============

Get the Code
------------

::

   git clone https://github.com/openstack/monasca-vagrant

Install Vagrant
---------------

Install VirtualBox and Vagrant
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Note: Vagrant version 1.5.0 or higher is required.

MacOS
^^^^^

The following steps assume you have `Homebrew`_ installed. Otherwise,
install `VirtualBox`_ and `Vagrant`_ and `Ansible`_ as suggested on
their websites.

::

   brew tap phinze/cask
   brew install brew-cask
   brew cask install virtualbox
   brew cask install vagrant
   brew install ansible  # Version 1.8+ is required
   ansible-galaxy install -r requirements.yml -p ./roles

Linux (Ubuntu)
^^^^^^^^^^^^^^

::

   sudo apt-get install virtualbox
   #Download and install latest vagrant from http://www.vagrantup.com/downloads.html
   sudo pip install ansible  # Version 1.8+ is required
   ansible-galaxy install -r requirements.yml -p ./roles

Using Monasca Vagrant
=====================

Starting mini-mon
-----------------

-  After installing to start just run ``vagrant up``. The first run will
   download required vagrant boxes.
-  When done you can run ``vagrant halt`` to stop the boxes and later
   run ``vagrant up`` to turn them back on. To destroy and rebuild run
   ``vagrant destroy -f``. It is typically fastest to use halt/up than
   to rebuild your vm.
-  Run ``vagrant help`` for more info on standard vagrant commands.

Basic Monasca usage
-------------------

The full Monasca stack is running on the mini-mon vm and many devstack
services on the devstack vm. A monasca-agent is installed on both and
metrics are actively being collected. - You can access the horizon UI by
navigating to http://192.168.10.5 and logging in as mini-mon/password.
This is the UI used for devstack and it contains the Monasca plugin
found at the Monitoring tab as well as Grafana used for graphing
metrics. - Run ``vagrant ssh <host>`` to log in, where ``<host>`` is
either ``mini-mon`` or ``devstack`` - The monasca cli is installed
within both vms and the necessary environment variables loaded into the
shell. This is a good way to explore the metrics in the system. For
example to list all metrics, run ``monasca metric-list``

Smoke test
----------

At the end of the install a smoke test is run that exercises every major
piece of Monasca. If this fails the end of the provision will report it.
It is possible to rerun this at any point using Ansible
``ansible-playbook ./smoke.yml`` or from within the vm by running
smoke.py and smoke2.py in
``/opt/monasca/hpcloud-mon-monasca-ci\*/tests/smoke``.

Updating
--------

When someone updates the config, this process should allow you update
the VMs, though not every step is needed at all times.

-  ``git pull``
-  ``ansible-galaxy install -r requirements.yml -p ./roles -f``
-  ``vagrant box update`` Only needed rarely
-  ``vagrant provision``, if the vms where halted run ``vagrant up``
   first.

   -  It is also possible to Ansible directly to update just parts of
      the system. See `Ansible Development`_ for more info.

Running behind a Web Proxy
--------------------------

If you are behind a proxy you can install the ``vagrant-proxyconf``
plugin to have Vagrant honor standard proxy-related environment
variables and set the VM to use them also. It is important that
192.168.10.4, 192.168.10.5, 127.0.0.1 and localhost be in your no_proxy
environment variable.

::

   vagrant plugin install vagrant-proxyconf

Running with Vertica
--------------------

You can configure Vagrant to run Vertica as the database in place of
influxdb.

To accomplish this you have to download the community edition (Debian)
and the jdbc driver from `Vertica`_.

Place the jdbc driver and debian in the home directory of vagrant with
the names of:

vertica_jdbc.jar vertica.deb

Set the environment variable USE_VERTICA to true and then run vagrant
up.

::

   export USE_VERTICA=true
   vagrant up

Advanced Usage
==============

Access information
------------------

-  Your host OS home dir is synced to ``/vagrant_home`` on the VM.
-  The root dir of the monasca-vagrant repo on your host OS is synced to
   ``/vagrant`` on the VM.
-  mini-mon is at 192.168.10.4 and devstack is at 192.168.10.5

Internal Endpoints
~~~~~~~~~~~~~~~~~~

-  Influxdb web ui is available at http://192.168.10.4:8083 with
   root/root as user/password
-  The Monasca-api is available at http://192.168.10.4:8070

   -  The keystone credentials used are mini-mon/password in the
      mini-mon project. The keystone services on 192.168.10.5 on
      standard ports.

Improving Provisioning Speed
----------------------------

The slowest part of the provisioning process is the downloading of
packages. The Vagrant plugin ``vagrant-cachier`` available at
https://github.com/fgrehm/vagrant-cachier should help by caching
repeated dependencies. To use with Vagrant simply install the plugin.

::

   sudo vagrant plugin install vagrant-cachier

Monasca Debugging
=================

See this page for details on the `Monasca Architecture`_.

The components of the system which are part of the Monasca code base
have there configuration in ``/etc/monasca`` and their logs in
``/var/log/monasca``. For nearly all of these you can set the logging to
higher debug level and restart. The components of the system which are
dependencies for Monasca (zookeeper, kafka, storm, influxdb, mysql) are
either in the standard Ubuntu location or in ``/opt``.

Some other helpful commands: - Zookeeper shell at -
``/usr/share/zookeeper/bin/zkCli.sh`` - Kafka debug commands are at
``/opt/kafka/bin`` in particular the ``kafka-console-consumer.sh`` is
helpful. - Running ``monasca-collector info`` will give an report on the
current state of agent checks. - The storm admin webui exists at
``http://192.168.10.4:8088`` - The mysql admin is root/password so you
can access the db with the command ``mysql -uroot -ppassword mon``

Ansible Development
-------------------

Running Ansible directly
~~~~~~~~~~~~~~~~~~~~~~~~

At any point you can rerun ``vagrant provision`` to rerun the Ansible
provisioning. Often it is easier to run ansible directly and specify
tags, ie ``ansible-playbook mini-mon.yml --tags api,persister``. Also a
very simple playbook is available for running the smoke test,
``ansible-playbook ./smoke.yml``

For these to work smoothly add these vagrant specific settings to your
local ansible configuration (~/.ansible.cfg or a personal ansible.cfg in
this dir):

::

   [defaults]
   hostfile = .ansible_hosts

   # In some configurations this won't work, use only if your config permits.
   [ssh_connection]
   pipelining = True  # Speeds up connections but only if requiretty is not enabled for sudo

Next run ``vagrant ssh-config >> ~/.ssh/config``, that will set the
correct users/host_keys for the vagrant vms.

When running Ansible directly make sure that you pass in what the
database_type is, ie
``ansible-playbook mini-mon.yml -e 'database_type=influxdb'``.

Editing Ansible Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Since there are only two VMs in this setup the Ansible configuration has
no host or group variables, rather all variables are in the playbook.
There is one playbook for each machine, ``mini-mon.yml`` and
``devstack.yml``. The playbooks contain all variables, some tasks and
the roles used in building the VMs.

To edit the Ansible roles I suggest downloading the full git source of
the role and putting it in your ansible path. This allows you to run
your changes directly from the git copy you are working on. See the
`Ansible docs`_ for more details on the exact configuration needed.

Developing Monasca
==================

In this repo there are a couple of helper scripts to aid in downloading
all of the Monasca git repositories. -
``./monasca-repos.sh <parent_dir>`` will clone all code repos to the
parent dir - ``./monasca-ansible-repos.sh <parent_dir>`` will clone all
code repos to the parent dir -
``./monasca-ansible-repos.sh <parent_dir>`` will clone all of the team
Ansible repos to the parent dir.

Alternate Vagrant Configurations
================================

To run any of these alternate configs, simply run the Vagrant commands
from within the subdir.

.. _Installation: #installation
.. _Get the Code: #get-the-code
.. _Install Vagrant: #install-vagrant
.. _Install VirtualBox and Vagrant: #install-virtualbox-and-vagrant
.. _MacOS: #macos
.. _Linux (Ubuntu): #linux-ubuntu
.. _Using Monasca Vagrant: #using-monasca-vagrant
.. _Starting mini-mon: #starting-mini-mon
.. _Basic Monasca usage: #basic-monasca-usage
.. _Smoke test: #smoke-test
.. _Updating: #updating
.. _Running behind a Web Proxy: #running-behind-a-web-proxy
.. _Running with Vertica: #running-with-vertica
.. _Advanced Usage: #advanced-usage
.. _Access information: #access-information
.. _Internal Endpoints: #internal-endpoints
.. _Improving Provisioning Speed: #improving-provisioning-speed
.. _Monasca Debugging: #monasca-debugging
.. _Ansible Development: #ansible-development
.. _Running Ansible directly: #running-ansible-directly
.. _Editing Ansible Configuration: #editing-ansible-configuration
.. _Developing Monasca: #developing-monasca
.. _Alternate Vagrant Configurations: #alternate-vagrant-configurations
.. _Troubleshooting: #troubleshooting
.. _Homebrew: http://brew.sh/
.. _VirtualBox: http://www.virtualbox.org
.. _Vagrant: http://www.vagrantup.com
.. _Ansible: http://www.ansible.com
.. _Vertica: https://my.vertica.com/download-community-edition/
.. _Monasca Architecture: https://wiki.openstack.org/wiki/Monasca
.. _Ansible docs: http://docs.ansible.com