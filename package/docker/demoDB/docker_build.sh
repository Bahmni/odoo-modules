#!/bin/bash
set -xe

#Fetching Database Backup Data
gunzip -f -k ../bahmni-scripts/demo/db-backups/v0.92/odoo_backup.sql.gz
cp ../bahmni-scripts/demo/db-backups/v0.92/odoo_backup.sql package/resources/odoo_demo_dump.sql

#Building Docker images
cd package
ODOO_IMAGE_TAG=${BAHMNI_VERSION}-${GITHUB_RUN_NUMBER}
docker build -t bahmni/odoo-10-db:demo-${ODOO_IMAGE_TAG} -t bahmni/odoo-10-db:demo-latest -f docker/demoDB/Dockerfile  . --no-cache
