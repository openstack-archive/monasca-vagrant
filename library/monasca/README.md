# ansible-module-monasca
Ansible module for crud operations on Monasca alarm definitions

Example usage

    tasks:
      - name: Create System Alarm Definitions
        monasca_alarm_definition:
          name: "{{item.name}}"
          expression: "{{item.expression}}"
          keystone_url: "{{keystone_url}}"
          keystone_user: "{{keystone_user}}"
          keystone_password: "{{keystone_password}}"
        with_items:
          - { name: "High CPU usage", expression: "avg(cpu.idle_perc) < 10 times 3" }

More information on [Monasca](https://wiki.openstack.org/wiki/Monasca)
