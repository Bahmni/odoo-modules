#!/bin/bash
set -xe

#Building Docker images
cd package
ODOO_IMAGE_TAG=${BAHMNI_VERSION}-${GITHUB_RUN_NUMBER}
docker build -t bahmni/odoo-10-db:fresh-${ODOO_IMAGE_TAG} -t bahmni/odoo-10-db:fresh-latest -f docker/freshDB/Dockerfile  . --no-cache
