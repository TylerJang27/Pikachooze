#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

source ../.flaskenv
dbname=$DB_NAME
if [[ -n `psql -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    if [[ `psql -d "$dbname" -c 'SELECT COUNT(*) FROM users' | sed -n 3p` -eq 0 ]]; then
        psql -af load.sql $dbname
    else
        echo "data already loaded"
    fi
else
    echo "database $dbname does not exist"
fi
