#!/bin/sh

if [ ! -f /usr/src/app/installed ]; then
    python ./manage.py migrate
    python ./manage.py loaddata LicenceClasses
    python ./manage.py loaddata Categories

    touch /usr/src/app/installed
fi

gunicorn --bind=0.0.0.0:8000 hackathon.wsgi
