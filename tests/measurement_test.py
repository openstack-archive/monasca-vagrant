#!/usr/bin/env python
#
"""measurements
"""
from __future__ import print_function
import sys
import time
import pytz
from datetime import datetime
from monascaclient import client
import monascaclient.exc as exc
import utils


def call_mon_api(method, fields):
    try:
        resp = method(**fields)
    except exc.HTTPException as he:
        print(he.code)
        print(he.message)
        sys.exit(1)
    else:
        return resp


def create_timestamp(seconds):
    utcTimestamp = pytz.utc.localize(datetime.utcfromtimestamp(seconds))
    return utcTimestamp.strftime("%Y-%m-%dT%H:%M:%S%z")


def main():
    if len(sys.argv) == 1:
        print('usage: %s metric_name count' % sys.argv[0], file=sys.stderr)
        return 1

    mon_client = utils.create_mon_client()

    metric_start_time = time.time()
    metric_name = sys.argv[1]
    num_metrics_to_send = int(sys.argv[2])
    dimensions = {'Test_Send': 'Number_1'}  # Should be arg
    start_time = time.time()
    fields = {'name': metric_name}
    fields['dimensions'] = dimensions
    for val in range(0, num_metrics_to_send):
        fields['value'] = str(val)
        fields['timestamp'] = time.time()
        call_mon_api(mon_client.metrics.create, fields)
        # time.sleep(1)

    print("Took %d seconds to send %d measurements" %
          ((time.time() - start_time), num_metrics_to_send))
    metric_end_time = time.time()
    # API requires end time to be greater than start time
    if (metric_end_time - metric_start_time) < 1:
        metric_end_time = metric_start_time + 1
    start_timestamp = create_timestamp(metric_start_time)
    end_timestamp = create_timestamp(metric_end_time)
    fields = {'name': metric_name}
    fields['dimensions'] = dimensions
    fields['start_time'] = start_timestamp
    fields['end_time'] = end_timestamp
    for i in range(0, 30):
        result = call_mon_api(mon_client.metrics.list_measurements, fields)
        if len(result) > 0:
            measurements = result[0]['measurements']
            if len(measurements) >= num_metrics_to_send:
                break
            print('Found %d of %d metrics so far' %
                  (len(measurements), num_metrics_to_send))
        time.sleep(1)

    if len(result) == 0:
        print('Did not receive any metrics in %d seconds' % i, file=sys.stderr)
        return 1

    if len(measurements) != num_metrics_to_send:
        print('Expected %d measurements but found %d' %
              (num_metrics_to_send, len(measurements)), file=sys.stderr)
        return 1
    print('Took %d seconds for metrics to fully arrive' % i)
    expected = num_metrics_to_send - 1
    result = 0
    for index in range(num_metrics_to_send, 0):
        value = measurements[index]
        if value[2] != expected:
            print('Expected %d but found %d for %d' %
                  (expected, value[2], index), file=sys.stderr)
        expected = expected - 1
    return result


if __name__ == "__main__":
    sys.exit(main())
