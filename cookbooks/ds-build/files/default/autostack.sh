#!/usr/bin/env bash

# Change Internal Field Separator to split on newlines only
IFS="
"

unpriv_user=$1
basedir="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
log='/opt/stack/logs/stack.sh.log'

usage="Usage: autostack.sh [username]
 where [username] is an unprivileged user under whom all DevStack
 processes will run."

if [ "$UID" != 0 ]; then
    echo "Please run this script as root or under sudo so that it can write to"
    echo " the /etc/init/ directory and start up the services."
    echo
    echo "$usage"
    exit 1
fi

if [ -z "$1" -o "$1" = "-h" -o "$1" = "--help" ]; then
    echo "$usage"
    exit 1
fi

cd $basedir
echo "Cloning devstack"
su $unpriv_user -c "git clone https://github.com/openstack-dev/devstack.git || exit 1"

echo "Copying local.conf"
cp $basedir/local.conf $basedir/devstack


# Kick off stack.sh in the background
echo "Running stack.sh (this will take a while, output in $log)"
su $unpriv_user -c $basedir/devstack/stack.sh 2>&1 &

# Wait for stack.sh to complete by watching the log file for $donestring
donestring='This is your host ip'

while [ `tail -1 $log 2>/dev/null |grep -c "$donestring"` = 0 ]; do
        sleep 5
done

# Kill off the now-idle stack.sh process
pkill -f devstack/stack.sh


if [ ! -e $basedir/devstack/stack-screenrc ]; then
    echo "$basedir/devstack/stack-screenrc not found.  Did stack.sh fail?"
    exit 1
fi


for line in `cat $basedir/devstack/stack-screenrc |tr -d "\r"`; do
    if  [[ $line == stuff* ]]; then
echo
        # Extract the command line to run this service
        command=`echo "$line" |sed 's/^stuff //;s/"//g'`
        base_command=`echo $command |sed 's:.*bin/::;s/ .*//'`

        # Skip screen sessions that are only a tail command
        [[ $command == *tail* ]] && continue

	# Ceilometer's stack-screenrc invocation differs from all the others
	if [ `echo "$command" |grep -c ceilometer` = 1 ]; then
		base_command=`echo $command |sed "s/cd ; //;s/ libvirtd '//;s/ .*//"`
		parent='/opt/stack/ceilometer'
	else
        	# Determine an appropriate log directory
        	parent=`echo "$command" |cut -d' ' -f2 |sed 's/;//'`
	fi
        logdir="/var/log/`basename $parent`"
        logfile="$base_command.log"

        echo "Creating /etc/init/$base_command.conf"

        cat > "/etc/init/$base_command.conf" <<EOF
description "$base_command server"

start on (filesystem and net-device-up IFACE!=lo)
stop on runlevel [016]

pre-start script
    mkdir -p $logdir
    chown $unpriv_user:root $logdir
end script

respawn

exec su -c "$command --log-dir=$logdir --log-file=$logfile" $unpriv_user
EOF
    # Swift processes do not support logfiles, so modify the init script
    if [ `echo "$command" |grep -c swift` = 1 ]; then
        sed -i 's/--log.*"/"/' /etc/init/$base_command.conf
    fi
    # Fire up the service
    service $base_command restart
    fi
done

echo "autostack.sh complete, no errors."
exit 0
