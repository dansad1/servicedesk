#!/bin/bash

# Start MySQL service
/etc/init.d/mysql start

# Load data from db_dump.json into MySQL database
mysql -h localhost -u root -p"${MYSQL_ROOT_PASSWORD}" "${MYSQL_DATABASE}" < /db_dump.json

# Keep the container running
exec "$@"
