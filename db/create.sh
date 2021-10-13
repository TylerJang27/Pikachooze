#!/bin/bash

mypath=`realpath $0`
mybase=`dirname $mypath`
cd $mybase

source ../.flaskenv
dbname=$DB_NAME
if [[ -n `psql -lqt | cut -d \| -f 1 | grep -w "$dbname"` ]]; then
    echo "Database $dbname already exists"
else
    createdb $dbname
fi
