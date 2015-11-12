#!/bin/sh
#
# Clone all the monasca code repos to $1

monasca_repos='https://github.com/openstack/monasca-agent.git
https://github.com/openstack/monasca-api.git
https://github.com/openstack/monasca-log-api.git
https://github.com/openstack/monasca-common.git
https://github.com/openstack/monasca-notification.git
https://github.com/openstack/monasca-persister.git
https://github.com/openstack/monasca-thresh.git
https://github.com/openstack/monasca-ui.git
https://github.com/openstack/python-monascaclient.git
https://github.com/hpcloud-mon/grafana
https://github.com/hpcloud-mon/monasca-tempest.git
https://github.com/FujitsuEnablingSoftwareTechnologyGmbH/logstash-output-monasca_api.git
https://github.com/FujitsuEnablingSoftwareTechnologyGmbH/kibana.git'

# Other repos not in the standard list are found at
# https://github.com/hpcloud-mon and https://github.com/openstack?query=monasca

if [ $# -ne 1 ]; then
  echo 'Usage: $0 <parent_dir>'
  echo 'This script will clone all Monasca repos to the supplied parent_dir'
  exit 1
fi

mkdir -p $1
cd $1
for repo in $monasca_repos; do
  git clone $repo
done
