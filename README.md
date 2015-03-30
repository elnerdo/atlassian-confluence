## Atlassian confluence

For more information on the app please refere to the offical
Atlassian websites:


- [confluence](https://www.atlassian.com/software/confluence)

### Prerequisites

TBD

### Deploy/Update the application

    # rebuild the docker images
    $ docker-compose build

    # restart the docker images
    $ docker-compose up -d

    # inspect the logs
    $ docker-compose logs

If you deploy the app for the first time you may need to restore the database
from a backup!

### Debug (aka. go inside) an image

    # execute a bash shell
    $ docker exec -it confluence_confluence_1 bash

### First run

If you start this orchestration for the first time, a handy feature is to
import your old data. If you're e.g. moving everything to another server
you can put your database backups into the tmp folder and the db initscript
will pick them up automagically on the first run if there is no `data` folder


    1. Approach with a dump file and tgz archive

    # move your confluence db backup file to tmp (filename is important).
    $ mv confluence.dump tmp/confluence.dump

    # unpack your confluence-home backup archive
    $ tar xzf confluence-home.tgz --strip=1 -C home


    2. Approach with bup

    # remove theses folder if present:
    $ data/ tmp/ home/ dumps/

    # move contents from the bup backup.
    $ sudo mv confluencebackup/confluence/* /srv/data/confluence

### Restore the PostgreSQL data

To restore the postresql data you have two options:

    1. Remove the `data` folder and put the dumpfile into `tmp`
    2. Replace the `data` folder with a bup backuped `data` folder

## Restoring with the fabfile or bup

    # All commands have to be launched from within the root folder of the app.
    $ /srv/data/confluence

Once you have run the restore command, you have to remove `data/ tmp/ dumps/ home/`
Move the folders from the created confluencebackup folder into the app root (where the deleted folders used to be).

### Show all possible restore points:

    sudo BUP_DIR=$(pwd)/backup bup ls confluencebackup`

### Restore latest backup:

    # With the fabfile:
    $ sudo fab restore

    # Without the fabfile:
    $ sudo BUP_DIR=$(pwd)/backup bup restore

### Restore a specific backup:

    # With the fabfile:
    $ sudo fab restore:revision='2015-03-26-123711'

    # Without the fabfile:
    $ sudo BUP_DIR=$(pwd)/backup bup restore confluencebackup/2015-03-26-123711/$(pwd)

### Restore to a different folder than confluencebackup

By default bup will restore the backup to a folder called confluencebackup.
To restore to another folder you can use the `-C` flag or pass `'destination'`
to the fabfile.

    # With the fabfile:
    $ sudo fab restore:destination='anotherlocation'

    # Without the fabfile:
    $ sudo BUP_DIR=$(pwd)/backup bup restore -C anotherlocation confluencebackup/latest/$(pwd)
