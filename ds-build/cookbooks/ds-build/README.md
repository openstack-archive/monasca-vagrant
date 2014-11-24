ds-build cookbook
=========================
Builds a Devstack VM around Ubuntu Trusty

This box is used by the Monasca OpenStack monitoring platform.
Based on Ubuntu 14.04 LTS (Trusty Tahr), the box includes
DevStack with the following services enabled:

- Ceilometer
- Cinder
- Glance
- Heat
- Horizon
- Keystone
- Neutron
- Nova
- Swift

Additionally, rather than running in screen sessions, all services are started
on boot using Upstart scripts, with logging in appropriate directories under
`/var/log/`.


Requirements
------------

Recipes
---------
- default - Installs devstack from source, creates upstart scripts
