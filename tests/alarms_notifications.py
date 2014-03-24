#!/usr/bin/env python
#
"""alarm_notification_setup
    Sets up test alarms and notifications using the mon-api. Assumes the mini-mon setup.
"""

import argparse
from glob import glob
import httplib
import json
import sys

API_HOST = '192.168.10.4'
API_PORT = '8080'
HEADERS = {"Content-Type": "application/json",
           "Accept": "application/json",
           "X-Tenant-Id": "1"}


def post(conn, url, body):
    conn.request("POST", url, body, HEADERS)
    http_response = conn.getresponse()
    response = http_response.read()
    if http_response.status < 200 or http_response > 300:
        print("\tError %d response: %s" % (http_response.status, response))
    return response

def main():
    parser = argparse.ArgumentParser(description='Setup Alarms and Notification via the api. Assumes mini-mon')
    parser.add_argument('--email', '-e', required=True)
    args = parser.parse_args()

    conn = httplib.HTTPConnection(API_HOST, API_PORT)

    with open('notification.json', 'r') as notification_file:
        notification_json = notification_file.read() % args.email

    print('Adding email notification.')
    response = post(conn, '/v2.0/notification-methods', notification_json)
    response_json = json.loads(response)

    notification_method_id = response_json['id']

    for path in glob('alarms/*.json'):
        with open(path, 'r') as alarm_file:
            alarm_json = alarm_file.read() % (notification_method_id, notification_method_id, notification_method_id)
        print('Adding Alarm %s' % path)
        post(conn, '/v2.0/alarms', alarm_json)

if __name__ == "__main__":
    sys.exit(main())
