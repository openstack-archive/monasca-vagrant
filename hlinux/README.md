An experimental hLinux based mini-mon is available for testing.

# Running hLinux as the base OS
hLinux can be installed and run as the base OS for all the vm(s) defined in mini-mon. The vagrantfile in this sub-dir is setup for this purpose.
Before running this you must create a hLinux box as describe below.

As of the last testing there are a couple of minor problems:
- The vboxsf filesystem driver is not working correctly in hLinux, this prevents home directory syncing.
- Slow network performance of the hLinux vbox image makes some tasks annoying.

## Creating a new hLinux box
The [hLinux](http://hlinux-home.usa.hp.com/wiki/index.php/Main_Page) box used in mini-mon is created via [packer](http://www.packer.io/), config is in
the templates sub-directory.

- Install packer
  - `brew tap homebrew/binary`
  - `brew install packer`
- Run packer
  - `cd templates`
  - `packer build hlinux.json`
- From the mini-mon directory run `vagrant box add hlinux templates/packer_virtualbox-iso_virtualbox.box`
  - If you have an existing hLinux box you man need to first remove it `vagrant box remove hlinux`
  - Also upload to a server for others to download.
