#!/bin/bash

while ! mysqladmin ping -h"$DB_HOST" --silent; do
    sleep 1
done

if [ ! -f /usr/src/app/installed ]; then
    python ./manage.py migrate
    python ./manage.py loaddata LicenseClasses
    python ./manage.py loaddata Categories

    touch /usr/src/app/installed
fi

gunicorn --bind=0.0.0.0:8000 hackathon.wsgi
