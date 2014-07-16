The chef and Vagrant configuration here runs mini-mon split into 6 different VMs. This split demonstrates and provides a simple test of how the
monitoring system can scale but also is useful for some development scenarios.

# Using the split mini-mon
- Your home dir is synced to `/vagrant_home` on each vm
- Vms created
  - `api` at `192.168.10.4`
  - `kafka` at `192.168.10.10` - mon-notification runs on this box also
  - `mysql` at `192.168.10.6`
  - `persister` at `192.168.10.12`
  - `thresh` at `192.168.10.14`
  - `vertica` at `192.168.10.8`
    - The management console is at https://192.168.10.8:5450
  - `devstack` at `192.168.10.5`
    - The web interface is at http://192.168.0.5
    - username `admin`, password `admin`
- Run `vagrant help` for more info
- Run `vagrant ssh <vm name>` to login to a particular vm
- Can also run `ssh vagrant@<ip address>` to login 
  - password is `vagrant`
  
## Start mini-mon
From within this directory, run this simple scripts which aid in bringing up all the vms in the proper order.
If desired, the standard vagrant commands can also be used.
```
bin/vup
```

## Halt mini-mon
In some cases halting mini-mon can result in certain vms being left in an odd state, to avoid this a script has been made to halt boxes in the 
correct order
```
bin/vhalt
```

