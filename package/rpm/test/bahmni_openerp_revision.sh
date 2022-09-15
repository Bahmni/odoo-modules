#!/usr/bin/env bash

revision='{
    "github_actions" : "https://github.com/Bahmni/odoo-modules/actions/runs/GITHUB_RUN_ID/",
    "github": {
        "odoo_modules" : "https://github.com/Bahmni/odoo-modules/commit/_modulesSha_"
    }
}'

replace() {
    envValue=`env | egrep "$2=" | sed "s/$2=//g"`
    sed "s/$1/$envValue/g"
}

echo $revision | replace "GITHUB_RUN_ID" "GITHUB_RUN_ID" | replace "_modulesSha_" "GITHUB_SHA"
