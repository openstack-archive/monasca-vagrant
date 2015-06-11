#!/opt/monasca/bin/python
#
from __future__ import print_function
import argparse
import kafka
import glob
import MySQLdb
from monascaclient import ksclient
import psutil
import requests
import shlex
import smoke2_configs
import socket
import subprocess
import sys
import utils

config = smoke2_configs.test_config
args = 0

# successfully = '\033[5;40;32mSuccessfully\033[0m'
# successful = '\033[5;40;32mSuccessful.\033[0m'
# error = '\033[5;41;37m[ERROR]:\033[0m'
successfully = 'Successfully'
successful = 'Successful.'
error = '[ERROR]'

# parse command line arguments
def parse_commandline_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-dbtype', '--dbtype',
                        default=config['default']['arg_defaults']['dbtype'],
                        help='specify which database (influxdb or vertica)')
    parser.add_argument('-k', '--kafka',
                        default=config['default']['arg_defaults']['kafka'],
                        help='will check kafka on listed node(s). '
                             'ex. -k "192.168.10.4 192.168.10.7"')
    parser.add_argument('-z', '--zoo',
                        default=config['default']['arg_defaults']['zoo'],
                        help='will check zookeeper on listed node(s). '
                             'ex. -z "192.168.10.4 192.168.10.7"')
    parser.add_argument('-m', '--mysql',
                        default=config['default']['arg_defaults']['mysql'],
                        help='will check mysql on listed node. '
                             'ex. -m "192.168.10.4"')
    parser.add_argument('-db', '--db',
                        help='will check database on listed node. '
                             'ex. -db "192.168.10.4"')
    parser.add_argument('-s', '--single',
                        help='will check all services on single node. '
                             'ex. -s "192.168.10.4"')
    parser.add_argument('-api', '--monapi',
                        default=config['default']['arg_defaults']['monapi'],
                        help='will check url api access on node. '
                             'ex. -api "192.168.10.4"')
    parser.add_argument('-v', '--verbose', action='store_true', default=0,
                        help='will display all checking info')
    return parser.parse_args()


def find_processes():
    """Find_process is meant to validate that all the required processes
    are running"""
    process_missing = []
    process_list = config['default']['check']['expected_processes']

    for process in process_list:
        process_found_flag = False

        for item in psutil.process_iter():
            for cmd in item.cmdline():
                if process in cmd:
                    process_found_flag = True
                    break

        if not process_found_flag:
            process_missing.append(process)

    if len(process_missing) > 0:   # if processes were not found
        print (error + ' Process = {} Not Found'
               .format(process_missing))
        return False
    print(successful + ' All Processes are running.')
    return True


def check_port(node, port):
    """Returns False if port is open (for fail check)"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((node, port))
    if result == 0:
        if args.verbose:
            print(successful + " Port {} is open".format(port))
        return False
    else:
        if args.verbose:
            print(error + " Port {} is not open".format(port))
        return True


def debug_kafka(node):
    print('********VERIFYING KAFKA NODE(S)********')
    node = node.split(' ')
    topics = config['default']['kafka']['topics']
    for nodeip in node:
        if nodeip[-5:-4] == ':':
            nodeip = nodeip[:-5]
        fail = check_port(nodeip, 9092)
        if args.verbose:
            print('Checking topics on node {}:'.format(nodeip))
        kafka_client = kafka.client.KafkaClient(nodeip + ':9092')
        for topic in topics:
            try:
                kafka.consumer.SimpleConsumer(
                    kafka_client,
                    'Foo',
                    topic,
                    auto_commit=True,
                    max_buffer_size=None)
                if args.verbose:
                    print('\t' + successfully + ' connected '
                                                'to topic {}'.format(topic))
            except KeyError:
                print('\t' + error + ' Could not connect '
                      'to topic {}'.format(topic))
                fail = True
    if fail:
        return False
    else:
        if not args.verbose:
            print(successful)
    return True


def debug_zookeeper(node):
    print('*******VERIFYING ZOOKEEPER NODE(S)*******')
    node = node.split(' ')
    for nodeip in node:
        if nodeip[-5:-4] == ':':
            nodeip = nodeip[:-5]
        fail = check_port(nodeip, 2181)
        cmd = "nc " + nodeip + ' 2181'
        ps = subprocess.Popen(('echo', 'ruok'), stdout=subprocess.PIPE)
        try:
            output = subprocess.check_output(shlex.split(cmd),
                                             stdin=ps.stdout)
            if output == 'imok':
                if args.verbose:
                    print("cmd: echo ruok | " + cmd + " Response: {}"
                          .format(output) + " " + successful)
                else:
                    print(successful)
        except subprocess.CalledProcessError:
            print(error + ' Node {} is not responding'.format(nodeip))
            return False
    if fail:
        return False
    return True


def debug_mysql(node, mysql_user, mysql_pass):
    print('********VERIFYING MYSQL NODE********')
    fail = check_port(node, 3306)
    schema = config['default']['mysql_schema']
    try:
        conn = MySQLdb.connect(
            host=node,
            user=mysql_user,
            passwd=mysql_pass,
            db='mon')
        if args.verbose:
            print(successfully + ' connected to node {}'.format(node))
        conn.query('show tables')
        result = conn.store_result()
        if args.verbose:
            print('Checking MYSQL Table Schema on node {}:'.format(node))
        for x in range(0, result.num_rows()):
            row = result.fetch_row()[0][0]
            if row in schema:
                if args.verbose:
                    print('\t' + successfully +
                          ' matched table {}'.format(row))
            else:
                print('\t' + error + ' Table {} does not '
                      'match config'.format(row))
                fail = True
        if fail:
            print('\033[5;41;37m[ERROR]: MySQL test failed\033[0m')
            return False
        else:
            if not args.verbose:
                print(successful)
        return True

    except MySQLdb.OperationalError, e:
        print(error + ' MySQL connection failed: {}'.format(e))
        return False


def debug_influx(node, influx_user, influx_pass):
    print('********VERIFYING INFLUXDB NODE********')
    try:
        from influxdb import client
    except ImportError, e:
        print("[WARNING]: InfluxDB Python Package is not installed!")
        return 1
    fail = check_port(node, 8086)
    fail = check_port(node, 8090)
    try:
        conn = client.InfluxDBClient(
            node,
            8086,
            influx_user,
            influx_pass,
            'mon'
        )
        conn.query('show series;')
        if args.verbose:
            print(successfully + ' connected to node {}'.format(node))
        else:
            print(successful)
    except Exception, e:
        print('{}'.format(e))
        return False
    if fail:
        return False
    return True


def debug_vertica(node, vuser, vpass):
    print('********VERIFYING VERTICA NODE********')
    fail = check_port(node, 5433)
    fail = check_port(node, 5434)
    try:
        cmd = "/opt/vertica/bin/vsql -U " + vuser + " -w  " + vpass + "  " \
              "-c \"select count(*) from MonMetrics.Measurements\""
        output = subprocess.check_output(shlex.split(cmd))
        if args.verbose:
            print("Running cmd: select count(*) from MonMetrics.Measurements")
            output = [int(s) for s in output.split() if s.isdigit()]
            print("Response: " + str(output[0]) + " " + successful)
        else:
            print(successful)
    except subprocess.CalledProcessError:
        print(error + " Cannot connect to vertica")
    if fail:
        return False
    return True


def debug_keystone(key_user, key_pass, project, auth_url):
    keystone = {
        'username': key_user,
        'password': key_pass,
        'project': project,
        'auth_url': auth_url
    }
    ks_client = ksclient.KSClient(**keystone)
    if args.verbose:
        print(successfully + ' connected to keystone with '
                             'token {}'.format(ks_client.token))
    else:
        print(successful)
    return ks_client.token


def debug_rest_urls(node, token):
    print('********VERIFYING REST API********')
    url = 'http://' + node + ":8080/"
    fail = check_port(node, 8080)
    try:
        r = requests.get(url, headers={'X-Auth-Token': token})
        if r.status_code == 200:
            version_id = r.json()['elements'][0]['id']
            if args.verbose:
                print(successfully + ' connected to REST API on '
                                     'node {}. Response (version id): {}'
                      .format(node, version_id))
            else:
                print(successful)
    except requests.ConnectionError:
        print(error + ' incorrect response from REST '
              'API on node {}'.format(node))
        return False
    if fail:
        return False
    else:
        return True


def debug_storm(node):
    print('********VERIFYING STORM********')
    fail = check_port(node, 6701)
    fail = check_port(node, 6702)
    fail = check_port(node, 6627)
    cmd = "/opt/storm/apache*"
    cmd = glob.glob(cmd)[0] + "/bin/storm list"
    grep = "grep 'ACTIVE'"
    try:
        ps = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        output = subprocess.check_output(shlex.split(grep), stdin=ps.stdout)
        if output:
            output = output[:27]
            output = " ".join(output.split())
            if args.verbose:
                print(successful + " Storm status: {}".format(output))
            else:
                print(successful)
    except Exception, e:
        print(error + " {}".format(e))
        return False
    if fail:
        return False
    else:
        return True


def stage_one(single=None, zoo=None, kafka=None):

    if single:
        debug_zookeeper(single)
    elif zoo:
        debug_zookeeper(zoo)
    else:
        print(error + ' Could not parse zookeeper node!')
        return 1

    if single:
        debug_kafka(single)
    elif kafka:
        debug_kafka(kafka)
    else:
        print(error + ' Could not parse kafka node!')
        return 1
    return 0


def stage_two(single=None, monapi=None):
    print('*****VERIFYING KEYSTONE*****')
    key_user = config['keystone']['user']
    key_pass = config['keystone']['pass']
    key_host = config['keystone']['host']
    if key_host:
        auth_url = "http://" + key_host + ':35357/v3'
        if key_user and key_pass:
            try:
                token = debug_keystone(key_user, key_pass, 'test', auth_url)
            except Exception, e:
                print(error + ' {}'.format(e))
                print('*****TEST FAILED*****')
                return 1
        else:
            print(error + ' Could not parse keystone user/pass')
            return 1
    else:
        print(error + ' Could not parse keystone node')
        return 1

    if single:
        debug_rest_urls(single, token)
    elif monapi:
        debug_rest_urls(monapi, token)
    else:
        print(error + ' Could not parse node for REST API')

    storm_node = config['storm']
    if storm_node:
        debug_storm(storm_node)
    else:
        print(error + ' Could not parse storm node')

def stage_three(single=None, mysql=None, dbtype=None, db=None):
    mysql_user = config['mysql']['user']
    mysql_pass = config['mysql']['pass']
    if mysql_user and mysql_pass:
        if single:
            debug_mysql(single, mysql_user, mysql_pass)
        elif mysql:
            debug_mysql(mysql, mysql_user, mysql_pass)
        else:
            print(error + ' Could not parse node for mysql')
            return 1
    else:
        print(error + ' Could not parse mysql user/pass')
        return 1

    if dbtype == 'vertica':
        vertica_user = config['vertica']['user']
        vertica_pass = config['vertica']['pass']
        vertica_node = config['vertica']['node']
        if vertica_user and vertica_pass:
            if single:
                debug_vertica(single, vertica_user, vertica_pass)
            elif db:
                debug_vertica(db, vertica_user, vertica_pass)
            else:
                debug_vertica(vertica_node, vertica_user, vertica_pass)
        else:
            print(error + ' Cloud not parse vertica user/pass')
            return 1
    else:
        influx_user = config['influx']['user']
        influx_pass = config['influx']['pass']
        influx_node = config['influx']['node']
        if single:
            debug_influx(single, influx_user, influx_pass)
        else:
            if db:
                debug_influx(db, influx_user, influx_pass)
            elif influx_node:
                if influx_node[0] == 'h':
                    influx_node = influx_node[7:-5]
                    debug_influx(influx_node, influx_user, influx_pass)
                else:
                    debug_influx(influx_node, influx_user, influx_pass)
            else:
                print(error + " Could not parse influxdb node")
                return 1


def main():
    utils.setup_cli()

    # parse the command line arguments
    global args
    args = parse_commandline_args()
    fail = 0

    # Stage One
    # Will check Zookeeper and Kafka
    fail = stage_one(args.single, args.zoo, args.kafka)

    print('*****VERIFYING HOST SERVICES/PROCESSES*****')
    if not find_processes():
        print('*****TEST FAILED*****')
        return 1

    # Stage Two
    # Will check keystone, REST API, and Storm
    fail = stage_two(args.single, args.monapi)

    # Stage Three
    # Will check MySQL and vertica/influxdb
    fail = stage_three(args.single, args.mysql, args.dbtype, args.db)

    if fail:
        print('*****TEST FAILED*****')
        return 1

    print('*****TEST FINISHED*****')
    return 0

if __name__ == "__main__":
    sys.exit(main())
