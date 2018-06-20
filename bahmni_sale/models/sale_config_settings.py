# -*- coding: utf-8 -*-
from odoo import models, fields, api


class SaleConfigSettings(models.TransientModel):
    _inherit = 'sale.config.settings'

    group_final_so_charge = fields.Boolean(string="Allow to enter final Sale Order charge",
                                           implied_group='bahmni_sale.group_allow_change_so_charge')
    group_default_quantity = fields.Boolean(string="Allow to enter default quantity as -1",
                                            implied_group='bahmni_sale.group_allow_change_qty')
