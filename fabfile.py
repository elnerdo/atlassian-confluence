#!/usr/bin/env python

import os
import sys
import boto.ec2
import json
from fabric.api import local, task
from fabric.context_managers import shell_env


@task
def backup():
    stop_docker_container()
    do_psql_dump()
    bup_init()
    bup_index()
    do_bup_backup()
    do_snapshot()
    start_docker_container()


@task
def restore(destination='confluencebackup', revision='latest'):
    do_bup_restore(destination, revision)


def do_snapshot():
    with open('.aws-auth') as f:
        auth = json.load(f)
    os.environ['AWS_ACCESS_KEY_ID'] = auth['key_id']
    os.environ['AWS_SECRET_ACCESS_KEY'] = auth['secret_key']
    instance_id = local(
        'curl http://169.254.169.254/latest/meta-data/instance-id',
        capture=True)
    conn = boto.ec2.connect_to_region('eu-central-1')
    volumes = conn.get_all_volumes(
        filters={'attachment.instance-id': instance_id})

    backup_vol = None
    for vol in volumes:
        if vol.attach_data.device == '/dev/xvdh':
            backup_vol = vol
            break

    if backup_vol:
        conn.create_snapshot(backup_vol.id, description='confluence-data-snap')


def do_bup_backup():
    print('Running incremental backup')
    backuped = local('BUP_DIR=$(pwd)/backup bup save -n confluencebackup $(pwd)')
    if backuped.return_code != 0:
        print 'An error occurred while backing up. Aborting...'
        sys.exit(1)


def do_bup_restore(destination, revision):
    restored = local('BUP_DIR=$(pwd)/backup bup restore -C {0} '
                     'confluencebackup/{1}/$(pwd)'.format(destination, revision))
    if restored.return_code != 0:
        sys.exit(1)


def bup_init():
    initiated = local('BUP_DIR=$(pwd)/backup bup init')
    if initiated.return_code != 0:
        sys.exit(1)


def bup_index():
    indexed = local('BUP_DIR=$(pwd)/backup bup index --exclude-from '
                    '.bup.ignore $(pwd)')
    if indexed.return_code != 0:
        sys.exit(1)


def do_psql_dump():
    print 'dumping...'
    dumped = local('docker run -t --rm --link confluence_database_1:db '
                   '-v $(pwd):/tmp postgres sh -c \'pg_dump -U confluence -h '
                   '"$DB_PORT_5432_TCP_ADDR" -w confluence > /tmp/confluence.dump\'')

    if dumped.return_code != 0:
        sys.exit(1)

    if not os.path.exists(os.path.join(os.getcwd(), 'dumps')):
        local('mkdir dumps')
    local('mv confluence.dump dumps/confluence.dump')


def stop_docker_container():
    stopped = local('sudo docker-compose stop confluence')
    if stopped.return_code != 0:
        sys.exit(1)


def start_docker_container():
    started = local('sudo docker-compose start confluence')
    if started.return_code != 0:
        sys.exit(1)
