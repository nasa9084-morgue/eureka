#!/usr/bin/sh

if [ ! -e /var/run/eureka ]; then
    mkdir /var/run/eureka
fi

cd /root/eureka
uwsgi uwsgi.ini
