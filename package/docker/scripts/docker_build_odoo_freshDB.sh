#!/bin/bash
set -xe

#Building Docker images
cd package
ODOO_IMAGE_TAG=${BAHMNI_VERSION}-${GITHUB_RUN_NUMBER}
docker build -t bahmni/odoo-10-db:fresh-${ODOO_IMAGE_TAG} -f docker/db.Dockerfile  . --no-cache
