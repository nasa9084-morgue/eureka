#!/usr/bin/sh

if [ ! -e /var/run/eureka ]; then
    mkdir /var/run/eureka
fi

if [ ! -e /var/log/eureka ]; then
    mkdir /var/log/eureka
fi

if [ ! -e /root/eureka/app/static/css ]; then
    mkdir /root/eureka/app/static/css
fi

cd /root/eureka
/usr/local/bin/sass app/static/sass/style.scss app/static/css/style.css
/root/eureka/venv/bin/uwsgi uwsgi.ini
