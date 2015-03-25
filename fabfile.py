#!/usr/bin/env python

import os
import sys
from fabric.api import *
from fabric.context_managers import shell_env


if len(sys.argv) != 2:
    sys.stderr.write('Usage: fab <backup|restore>\n')
    sys.exit(1)
elif sys.argv[1] not in ['backup', 'restore']:
    sys.stderr.write('Usage: fab <backup|restore>\n')
    sys.exit(1)

psql_dump_cmd = 'docker run -it --rm --link confluence_database_1:db -v \
$(pwd):/tmp postgres sh -c \'pg_dump -U confluence -h "$DB_PORT_5432_TCP_ADDR"\
 -w confluence > /tmp/confluence.dump\''

bup_backup_cmd = 'BUP_DIR=$(pwd)/backup bup save -n confluencebackup $(pwd)'

bup_restore_cmd = 'BUP_DIR=$(pwd)/backup bup restore -C confluencebackup \
confluencebackup/latest/$(pwd)'


def backup():
    stop_docker_container()
    do_psql_dump()
    bup_init()
    bup_index()
    do_bup_backup()
    start_docker_container()
    return


def restore():
    do_bup_restore()
    return


def do_bup_backup():
    print("Running incremental backup")
    backuped = local(bup_backup_cmd)
    if backuped.return_code != 0:
        print 'An error occurred while backing up. Aborting...'
        sys.exit(1)
    return


def do_bup_restore():
    restored = local(bup_restore_cmd)
    if restored.return_code != 0:
        print 'An error occurred while restoring. Aborting...'
        sys.exit(1)
    return


def bup_init():
    initiated = local("BUP_DIR=$(pwd)/backup bup init")
    if initiated.return_code != 0:
        print 'An error occurred while initiating bup. Aborting...'
        sys.exit(1)
    return


def bup_index():
    indexed = local("BUP_DIR=$(pwd)/backup bup index --exclude-from \
.bup.ignore $(pwd)")
    if indexed.return_code != 0:
        print 'An error occurred while indexing bup. Aborting...'
        sys.exit(1)
    return


def do_psql_dump():
    result = local("ls $(pwd)/backup")
    if result.return_code != 0:
        local('mkdir $(pwd)/backup')
    print 'dumping...'
    dumped = local(psql_dump_cmd)
    if dumped.return_code != 0:
        print 'An error occured while dumping database. Aborting...'
        sys.exit(1)
    print 'dumped...'
    return


def stop_docker_container():
    print 'stoping...'
    stopped = local('sudo docker-compose stop confluence')
    if stopped.return_code != 0:
        print 'An error occurred while stoping container confluence. \
Aborting...'
        sys.exit(1)
    print 'stopped...'
    return


def start_docker_container():
    print 'starting...'
    started = local('sudo docker-compose start confluence')
    if started.return_code != 0:
        print 'An error occurred while starting container confluence. \
Aborting...'
        sys.exit(1)
    print 'started...'
    return
