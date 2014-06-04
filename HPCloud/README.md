# Mini-mon in the cloud
Run vagrant commands from this subdir to have Mini-mon run in the HP Public Cloud rather than as a vm on your machine.

You must have a valid HPCloud account with a defined security group that allows ssh access and an ssh key pair must be defined.

To setup:
- Install the plugin `vagrant plugin install vagrant-hp`
- Copy Vagrantfile.hpcloud to ~/.vagrant.d/Vagrantfile then edit and enter your credentials and other access information.

