#!/bin/sh
# launch-xnat.sh

set -e

until psql -U postgres -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 5
done


>&2 echo "Postgres is up - building XNAT database"
psql -U postgres -f /XNAT.sql

>&2 echo "Launching tomcat"
exec /usr/local/tomcat/bin/catalina.sh run