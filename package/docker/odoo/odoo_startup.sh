#!/bin/bash
set -e
odoo -d odoo -u ${MODULE} --db_host ${HOST} --db_password ${PASSWORD}