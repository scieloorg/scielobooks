#!/bin/sh

# Configuring Application conf
if [ -f /app/production.ini ]; then
    sed -i "s/fileserver_sync_enable = true/fileserver_sync_enable = $FILESERVER_SYNC_ENABLE/g" /app/production.ini
    sed -i "s/http:\/\/static.scielo.org\/scielobooks/$FILESERVER_URL/g" /app/production.ini
    sed -i "s/\/var\/www\/static_scielo_org\/scielobooks/$FILESERVER_REMOTEBASE/g" /app/production.ini
    sed -i "s/ip_server_static/$FILESERVER_HOST/g" /app/production.ini
    sed -i "s/user_server_static/$FILESERVER_USERNAME/g" /app/production.ini
    sed -i "s/pass_server_static/$FILESERVER_PASSWORD/g" /app/production.ini
    sed -i "s/sqlite:\/\/\/\%\(here\)s\/database.db/$SQLALCHEMY_URL/g" /app/production.ini
    sed -i "s/http\:\/\/img.livros.scielo.org\/books/$BOOKS_STATIC_URL/g" /app/production.ini
    sed -i "s/http\:\/\/iahx.local/$SOLR_URL/g" /app/production.ini
    sed -i "s/http\:\/\/127.0.0.1\:5984/$DB_URI/g" /app/production.ini
    sed -i "s/serve_static_files = true/serve_static_files = $SERVER_STATIC_FILES/g" /app/production.ini
    sed -i "s/mail_server_address/$MAIL_HOST/g" /app/production.ini
    sed -i "s/25/$MAIL_PORT/g" /app/production.ini
    sed -i "s/mail.username =/mail.username = $MAIL_USERNAME/g" /app/production.ini
    sed -i "s/mail.password =/mail.password = $MAIL_PASSWORD/g" /app/production.ini
    sed -i "s/mail.default_sender =/mail.default_sender = $MAIL_DEFAULT_SENDER/g" /app/production.ini
    sed -i "s/mail.tls = true/mail.tls = $MAIL_TLS/g" /app/production.ini
else
    echo 'Error: File not exists or/and variable not specified'
fi

# Run the gunicorn process in the foregroun
echo "[GUNICORN Startup] Starting..."
gunicorn --paste /app/production.ini
