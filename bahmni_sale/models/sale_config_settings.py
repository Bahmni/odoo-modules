# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_final_so_charge = fields.Boolean(string="Allow to enter final Sale Order charge",
                                           implied_group='bahmni_sale.group_allow_change_so_charge')
    group_default_quantity = fields.Boolean(string="Allow to enter default quantity as -1",
                                            implied_group='bahmni_sale.group_allow_change_qty')
    convert_dispensed = fields.Boolean(string="Allow to automatically convert "
                                       "quotation to sale order if drug is dispensed from local shop")
#     auto_convert_dispensed = fields.Selection([(0, "Allow to automatically convert "\
#                                        "quotation to sale order if drug is dispensed from local shop"),
#                                           (1, "Manually convert quotation to sale order")],
#                                          string="Convert Dispensed")

    @api.multi
    def set_convert_dispensed(self):
        return self.env['ir.values'].sudo().set_default(
            'sale.config.settings', 'convert_dispensed', self.convert_dispensed)
