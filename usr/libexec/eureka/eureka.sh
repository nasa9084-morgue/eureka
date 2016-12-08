#!/usr/bin/sh

if [ ! -e /var/run/eureka ]; then
    mkdir /var/run/eureka
fi

cd /root/eureka
/root/eureka/venv/bin/uwsgi uwsgi.ini
