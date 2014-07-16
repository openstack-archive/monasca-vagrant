The ds-build Vagrant profile installs the latest DevStack onto an Ubuntu
Trusty virtual machine, activating extra services and setting it up to
run out of Upstart rather than screen sessions.

Default admin credentials are username `admin` and password `admin`.

# Services Enabled
The following services are enabled:

- Ceilometer
- Cinder
- Glance
- Heat
- Horizon
- Keystone
- Neutron
- Nova
- Swift

Note that with Neutron, `Q_PLUGIN` is set to linuxbridge rather than
openvswitch.

# Upstart instead of screen

The cookbook includes a script which creates Upstart init scripts for each of
the services.  It also sets up log files in the `/var/log/` directory.  When
the VM is booted, all DevStack processes will start automatically.

# Usage

## Initial build
From within this directory, run this command to build the server:
`vagrant up`

The DevStack installation will take a long time, and you can follow its
progress from another terminal by running `vagrant ssh` and then
`tail -f /opt/stack/logs/stack.sh.log`

## Packaging for VagrantCloud
From within the `ds-build` directory, run this command to build a new
VagrantCloud box image after `vagrant up` completed successfully:
```
box='devstack.box'; [ -e ../$box ] && rm -v ../$box ; vagrant package devstack --output $box
```

