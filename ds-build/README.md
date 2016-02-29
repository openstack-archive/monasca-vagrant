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

# Upstart instead of screen

The Ansible role includes a script which creates Upstart init scripts for each
of the services.  It also sets up log files in the `/var/log/` directory.  When
the VM is booted, all DevStack processes will start automatically.

# Usage

## Initial build
From within this directory, run this command to build the server:
`vagrant up`

You may optionally change the devstack branch from which to build by editing
`devstack_branch` in `ds-build.yml`.

The DevStack installation will take a long time, and you can follow its
progress from another terminal by running `vagrant ssh` and then
`tail -F /opt/stack/logs/stack.sh.log`

## Packaging for HashiCorp Atlas (formerly VagrantCloud)
To ensure that this VM can provision its own instances, launch and delete
an instance prior to packging for VagrantCloud.
1. Open http://192.168.10.5 in a web browser 
2. Log in using default admin credentials specified above
3. Click on 'Project' at left, then 'Instances'
4. Click the 'Launch Instance' button
5. Enter an Instance Name, any name will do
6. Select Flavor 'm1.tiny'
7. Set Instance Boot Source to 'Boot from image'
8. Choose 'cirros' as the Image Name
9. Click the 'Launch' button
10. Once the image is created successfully, terminate it
11. Repeat steps 4-10 as needed for any other OS images
12. Sign out from the web interface; you are now ready to package the box image
13. From within the `ds-build` directory, run this command to build a new HashiCorp Atlas box image:
```
box='devstack.box'; [ -e ../$box ] && rm -v ../$box ; vagrant package devstack --output $box
```

## Deploying a new Monasca devstack box version
1. Rename devstack.box to include an incremented version number, as in `mv devstack.box devstack-0.2.1.box` (from the `monasca-vagrant` directory)
2. Log in to MediaFire account, click Upload, select 'Upload' -> 'From computer', click the + sign and select the new .box file, select 'Begin Upload'
3. Once uploaded, select the copy link icon to copy a direct download URL to the clipboard
4. Log in to [Hasicorp Atlas](https://atlas.hashicorp.com/session) as the 'monasca' user
5. Go to the [list of monasca/devstack box versions](https://atlas.hashicorp.com/monasca/boxes/devstack)
6. Select 'New version' on the left
7. Enter version number and a description, click 'Create version', then 'Create new provider'
8. Set 'Provider' to 'virtualbox', choose 'URL', and paste the file sharing URL copied from MediaFire, click 'Create provider'
9. Click on the text link 'unreleased', then 'Release version'
