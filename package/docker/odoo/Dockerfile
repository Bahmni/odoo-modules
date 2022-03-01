FROM odoo@sha256:7bbade53c6b07b5c31046ab5d85d9f7c9115d731ec585c2146b8005bb2944d39

ENV ADDON_PATH=/opt/bahmni-erp/bahmni-addons

COPY package/docker/odoo/odoo.conf /etc/odoo/odoo.conf
COPY bahmni_account ${ADDON_PATH}/bahmni_account/
COPY bahmni_atom_feed ${ADDON_PATH}/bahmni_atom_feed/
COPY bahmni_product ${ADDON_PATH}/bahmni_product/
COPY bahmni_purchase ${ADDON_PATH}/bahmni_purchase/
COPY bahmni_sale ${ADDON_PATH}/bahmni_sale/
COPY bahmni_stock ${ADDON_PATH}/bahmni_stock/
COPY bahmni_web_extension ${ADDON_PATH}/bahmni_web_extension/
COPY web_readonly_bypass ${ADDON_PATH}/web_readonly_bypass/