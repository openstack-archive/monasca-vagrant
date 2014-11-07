#Devstack
Configures certain Monasca Agent plugins to work on a Devstak VM

Plugins configured:
- MySQL
- RabbitMQ 

Usernames and passwords may need to be changed from defaults to reflect the
devstack environment:
- MySQL
  - mysql_user
  - mysql_pass
- RabbitMQ
  - rmq_user
  - rmq_pass
  - rmq_nodes
  - rmq_queues
  - rmq_exchanges

##Requirements
-  tkuhlman.monasca-agent

##Optional

##License
Apache

##Author Information
David Schroeder

Monasca Team email monasca@lists.launchpad.net
