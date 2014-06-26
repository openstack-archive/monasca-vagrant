#!/usr/bin/env bash

IFS="
"

unpriv_user=$USER
basedir=`dirname $0`

if [ ! -e $basedir/stack-screenrc ]; then
    echo "$basedir/stack-screenrc not found.  Did you run ./stack.sh?"
    exit 1
fi


for line in `cat $basedir/stack-screenrc |tr -d "\r"`; do
    if  [[ $line == stuff* ]]; then
        # Extract the command line to run this service
        command=`echo "$line" |sed 's/^stuff //;s/"//g'`
        base_command=`echo $command |sed 's:.*bin/::;s/ .*//'`

        # Skip screen sessions that are only a tail command
        [[ $command == *tail* ]] && continue

        # Determine an appropriate log directory
        parent=`echo "$command" |cut -d' ' -f2 |sed 's/;//'`
        logdir="/var/log/`basename $parent`"
        logfile="$base_command.log"

        echo "Creating /etc/init/$base_command.conf"

        sudo tee "/etc/init/$base_command.conf" >/dev/null <<EOF
description "$base_command server"
author "David Schroeder <david.schroeder@hp.com>"

start on (filesystem and net-device-up IFACE!=lo)
stop on runlevel [016]

pre-start script
    mkdir -p $logdir
    chown $unpriv_user:root $logdir
end script

respawn

exec su -c "$command --log-dir=$logdir --log-file=$logfile" $unpriv_user
EOF
    # Fire up the service
    service $base_command restart
    fi
done
