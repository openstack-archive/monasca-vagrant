#!/usr/bin/env python
#
""" Threshold Engine Test
    CRUD test
"""
from __future__ import print_function
import sys
import os
import time
import cli_wrapper
import utils


def output_metrics(alarm_id, expected_state, metrics):
    print('Generating metrics, waiting for state change to %s' %
          expected_state)
    hostnames = ['AA', 'BB', 'CC']
    for x in range(0, 90):
        for metric in metrics:
            metric_name = metric[0]
            dimensions = metric[1]
            args = ['metric-create', '--dimensions']
            hostname = hostnames[x % len(hostnames)]
            args.append(dimensions + ',' + 'hostname=' + hostname)
            args.append(metric_name)
            args.append('42')
            cli_wrapper.run_mon_cli(args, useJson=False)

        state = cli_wrapper.get_alarm_state(alarm_id)
        if state == expected_state:
            break
        time.sleep(1)

    if state != expected_state:
        print('Did not change to state %s instead was %s in %d seconds' %
              (expected_state, state, x), file=sys.stderr)
        return False

    print('Changed to state %s in %d seconds' % (state, x))
    return True


def main():
    utils.setup_cli()

    alarm_name = 'alarm_crud'
    metric_name = 'alarm_crud'
    base_dimension = 'service=alarm_test'
    expression = 'max(%s{%s}) > 0' % (metric_name, base_dimension)
    description = alarm_name + ' Description'
    cli_wrapper.delete_alarm_if_exists(alarm_name)

    # Add Alarm
    alarm_id = cli_wrapper.create_alarm(alarm_name, expression,
                                        description=description)
    print('Created Alarm with id %s' % alarm_id)

    # Ensure it is created in the right state
    initial_state = 'UNDETERMINED'
    if not utils.check_alarm_state(alarm_id, initial_state):
        return 1

    states = []
    states.append(initial_state)

    # List Alarms, make sure new one shows up
    alarm_json = cli_wrapper.find_alarm_by_name(alarm_name)
    if alarm_json is None:
        print('Did not find alarm named %s using alarm-list' %
              alarm_name, file=sys.stderr)
        return 1

    if alarm_id != alarm_json['id']:
        print('Alarm %s has wrong id, expected %s but was %s' %
              (alarm_name, alarm_id, alarm_json['id']), file=sys.stderr)
        return 1

    # Output metrics that will cause it to go ALARM
    # Wait for it to change to ALARM
    if not output_metrics(alarm_id, 'ALARM', [[metric_name, base_dimension]]):
        return 1

    states.append('ALARM')

    # Modify Alarm by adding new expression that will cause it to go OK
    print('Modify Alarm expression so it will go to OK')
    new_metric_name = 'other_metric'
    new_dimension = 'dim=42'
    new_expression = '%s and max(%s{%s}) > 100' % (expression,
                                                   new_metric_name,
                                                   new_dimension)

    alarm_json = cli_wrapper.patch_alarm(alarm_id, '--expression',
                                         new_expression)
    if alarm_json['expression'] != new_expression:
        print('Did not change expression to %s instead was %s' %
              (new_expression, alarm_json['expression']), file=sys.stderr)
        return 1

    # Output metrics that will cause it to go OK
    # Wait for it to change to OK

    if not output_metrics(alarm_id, 'OK', [[metric_name, base_dimension],
                                           [new_metric_name, new_dimension]]):
        return 1

    states.append('OK')

    # Modify Alarm by deleting expression that will cause Alarm to go ALARM
    print('Delete Alarm sub expression so it will go to ALARM')
    cli_wrapper.patch_alarm(alarm_id, '--expression', expression)

    # Output metrics that will cause it to go ALARM
    # Wait for it to change to ALARM
    print('Output extra dimensions to make sure match occurs')
    extra_dimension = base_dimension + ',Extra=More'
    if not output_metrics(alarm_id, 'ALARM',
                          [[metric_name, extra_dimension]]):
        return 1

    states.append('ALARM')

    # Modify Alarm by setting alarm state to OK
    print('Set Alarm to OK, wait for transition back to ALARM')

    cli_wrapper.change_alarm_state(alarm_id, 'OK')
    states.append('OK')

    # Output metrics that will cause it to go back to ALARM
    # Wait for it to change to ALARM
    if not output_metrics(alarm_id, 'ALARM',
                          [[metric_name, base_dimension],
                           [new_metric_name, new_dimension]]):
        return 1

    states.append('ALARM')

    # Query History
    # Delete ALARM
    print('Delete alarm')
    cli_wrapper.run_mon_cli(['alarm-delete', alarm_id], useJson=False)

    # Ensure it can't be queried
    if cli_wrapper.find_alarm_by_name(alarm_name) is not None:
        print('Still found alarm %s after it was deleted' % alarm_name,
              file=sys.stderr)
        return 1

    # Query History, ensure they still show up
    if not utils.check_alarm_history(alarm_id, states):
        return 1

    # Success
    return 0


if __name__ == "__main__":
    sys.exit(main())
