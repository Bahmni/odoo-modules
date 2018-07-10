# -*- coding: utf-8 -*-
from odoo import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    dhis2_code = fields.Char(string="DHIS Code")
    
#     def _compute_address(self):
#         for company in self.filtered(lambda company: company.partner_id):
#             address_data = company.partner_id.sudo().address_get(adr_pref=['contact'])
#             if address_data['contact']:
#                 partner = company.partner_id.browse(address_data['contact']).sudo()
#                 company.street = partner.street
#                 company.street2 = partner.street2
#                 company.city = partner.city
#                 company.zip = partner.zip
#                 company.state_id = partner.state_id
#                 company.country_id = partner.country_id
#                 company.fax = partner.fax