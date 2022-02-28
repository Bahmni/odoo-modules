#!/bin/bash
set -xe

cd package
# Unzipping Odoo Modules copied by CI
mkdir -p build/odoo-modules
unzip -q -u -d build/odoo-modules resources/odoo-modules.zip

#Building Docker images
ODOO_IMAGE_TAG=${BAHMNI_VERSION}-${GITHUB_RUN_NUMBER}
docker build -t bahmni/odoo-10:${ODOO_IMAGE_TAG} -t bahmni/odoo-10:latest -f docker/odoo/Dockerfile  . --no-cache
