# Setup of a test cluster

The goal of this fabric script is to setup a test cluster on baremetal leveraging some tools from mini-mon.

##Steps
- Before running first setup the following settings for your test cluster:
  - keystone host and project_id in data_bags/mon_agent/mon_agent.json
  - keystone host(serverVip) in data_bags/mon_api/mon_credentials.json
  - wsrep address in the Mon-Node role
  - servers in data_bags/zookeeper/mon.json
  - servers in data_bags/kafka/mon.json
  - vertica data bags in data_bags/vertica
    - ssh_key.json with two fields, public/private corresponding to public/private ssh keys
    - nodes data bag
- From the utils directory (or specifying that fabfile) start the install script
  - `fab cluster.setup -H host1,host2,host3`
  - 3 hosts is the minimum needed for a fully HA cluster.
  - All 3 machines will run the Mon-Node role, host1 will also run the Thresh-Nimbus role and remaining hosts the Thresh-Supervisor role
- After the cluster is up and running some additional configuration steps are needed to setup kafka topics and databases.
  - On one of the machines run the recipes:
    - kafka::create_topics
    - mini-mon::mysql_schema
    - vertica::create_db 

## Optional Configuration
- Add in the Vertica Console to one of the machines. This can be done with vertica::console recipe

## Known Issues
- runit used for the storm cookbook needs a newer version for chef 11 and even the newer version has errors on hLinux.
- If a client connects to kafka before the topics are made in some situations the topics are automatically created and can end up
  as the wrong size or without replicas.
- The percona cluster can be fickle regarding how to start it up properly this at times interferes with the cookbook. A workaround is
  to initially set the wsrep_cluster_address to just gcomm://
- Various cookbooks were pinned to older versions to accomodate the old chef used in the precise vagrant image, these can be unpinned.
