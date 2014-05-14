from __future__ import print_function

"""
    Utility methods for notifications
"""
import sys
import json
import subprocess


def find_notifications(alarm_id):
    args = ['sudo', 'cat', '/var/mail/root']
    result = []
    try:
        stdout = subprocess.check_output(args)
    except subprocess.CalledProcessError as e:
        print(e, file=sys.stderr)
        sys.exit(1)
    for line in stdout.splitlines():
        if alarm_id in line:
            result.append(json.loads(line)['state'])
    return result
