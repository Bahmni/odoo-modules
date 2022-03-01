FROM postgres:9.6-alpine

COPY package/resources/setupDB.sql /resources/setupDB.sql
COPY package/resources/odoo_clean_dump.sql /resources/odoo_clean_dump.sql
COPY package/docker/freshDB/configureDB.sh /docker-entrypoint-initdb.d/configureDB.sh