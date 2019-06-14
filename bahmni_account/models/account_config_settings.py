# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    round_off_by = fields.Float(string="Round off by", related="company_id.round_off_by")
    validate_picking = fields.Boolean(string="Validate Pickings when invoice is created",help="Product configuration must be Tacking='No Tracking' then this option will work")

    @api.multi
    def set_round_off_by_defaults(self):
        return self.env['ir.values'].sudo().set_default(
            'account.config.settings', 'round_off_by', self.round_off_by)
            
    @api.model
    def get_default_validate_picking(self, fields):
        value = int(self.env.ref('bahmni_account.validate_invoice_basedon_invoice').value)
        return {'validate_picking': bool(value)}

    @api.multi
    def set_default_validate_picking(self):
        for record in self:
            value = 1 if record.validate_picking else 0
            self.env.ref('bahmni_account.validate_invoice_basedon_invoice').write({'value': str(value)})

