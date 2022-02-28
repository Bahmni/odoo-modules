FROM postgres:9.6-alpine

COPY resources/setupDB.sql /resources/setupDB.sql
COPY resources/odoo_demo_dump.sql /resources/odoo_demo_dump.sql
COPY docker/demoDB/configureDemoDB.sh /docker-entrypoint-initdb.d/configureDemoDB.sh