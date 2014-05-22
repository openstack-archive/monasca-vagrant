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
- create kafka topics - kafka::create_topics recipe can be run on 1 machine
- Setup the Vertica database schema - the vertica::create_db recipe and scripts can be used for reference but won't work for a cluster
  - The problems with the script are:
    - The create_db command needs all ips specified for the -s arg, they are comma seperated
    - The symbolic linking of ssl cert/key needs to be done on each node
    - The restart policy should be set to ksafe rather than always
- Setup the mysql database schema - the mini-mon::mysql_schema tecipe can be run on 1 machine
- Restart any services which require vertica, mysql or kafka


## Optional Configuration
- Add in the Vertica Console to one of the machines. This can be done with vertica::console recipe
