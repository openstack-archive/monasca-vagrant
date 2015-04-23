#!/bin/sh
#
# Clone all the ansible code repos to $1

monasca_repos='https://github.com/hpcloud-mon/ansible-monasca-agent.git
https://github.com/hpcloud-mon/ansible-monasca-api.git
https://github.com/hpcloud-mon/ansible-monasca-default-alarms.git
https://github.com/hpcloud-mon/ansible-monasca-keystone.git
https://github.com/hpcloud-mon/ansible-monasca-notification.git
https://github.com/hpcloud-mon/ansible-monasca-persister.git
https://github.com/hpcloud-mon/ansible-monasca-schema.git
https://github.com/hpcloud-mon/ansible-monasca-thresh.git
https://github.com/hpcloud-mon/ansible-monasca-ui.git
https://github.com/hpcloud-mon/ansible-influxdb.git
https://github.com/hpcloud-mon/ansible-kafka.git
https://github.com/hpcloud-mon/ansible-percona.git
https://github.com/hpcloud-mon/ansible-storm.git
https://github.com/hpcloud-mon/ansible-zookeeper.git'

# Other repos not in the standard list are found at https://github.com/hpcloud-mon and https://github.com/stackforge?query=monasca

if [ $# -ne 1 ]; then
  echo 'Usage: $0 <parent_dir>'
  echo 'This script will clone all Monasca ansible repos to the supplied parent_dir'
  exit 1
fi

mkdir -p $1
cd $1
for repo in $monasca_repos; do
  git clone $repo
done
