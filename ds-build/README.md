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
- Nova
- Swift

# Upstart instead of screen

The Ansible role includes a script which creates Upstart init scripts for each
of the services.  It also sets up log files in the `/var/log/` directory.  When
the VM is booted, all DevStack processes will start automatically.

# Usage

## Initial build
From within this directory, run this command to build the server:
`vagrant up`

The DevStack installation will take a long time, and you can follow its
progress from another terminal by running `vagrant ssh` and then
`tail -f /opt/stack/logs/stack.sh.log`

## Packaging for VagrantCloud
To ensure that this VM can provision its own instances, launch and delete
an instance prior to packging for VagrantCloud.
- Open http://192.168.10.5 in a web browser 
- Log in using default admin credentials specified above
- Click on 'Project' at left, then 'Instances'
- Click the 'Launch Instance' button
- Enter an Instance Name, any name will do
- Select Flavor 'm1.tiny'
- Set Instance Boot Source to 'Boot from image'
- Choose 'cirros' as the Image Name
- Click the 'Launch' button
- Once the image is created successfully, terminate it
- Sign out from the web interface; you are now ready to package the box image

From within the `ds-build` directory, run this command to build a new
VagrantCloud box image:
```
box='devstack.box'; [ -e ../$box ] && rm -v ../$box ; vagrant package devstack --output $box
```

