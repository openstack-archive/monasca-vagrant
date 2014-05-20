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
- Setup the Vertica database schema
- Setup the mysql database schema
- Restart any services which require vertica or mysql

