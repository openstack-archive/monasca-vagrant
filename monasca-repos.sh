#!/bin/sh
#
# Clone all the monasca code repos to $1

monasca_repos='https://github.com/stackforge/monasca-agent.git
https://github.com/stackforge/monasca-api.git
https://github.com/stackforge/monasca-common.git
https://github.com/stackforge/monasca-notification.git
https://github.com/stackforge/monasca-persister.git
https://github.com/stackforge/monasca-thresh.git
https://github.com/stackforge/monasca-ui.git
https://github.com/stackforge/python-monascaclient.git
https://github.com/hpcloud-mon/grafana
https://github.com/hpcloud-mon/monasca-tempest.git'

# Other repos not in the standard list are found at https://github.com/hpcloud-mon and https://github.com/stackforge?query=monasca

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
