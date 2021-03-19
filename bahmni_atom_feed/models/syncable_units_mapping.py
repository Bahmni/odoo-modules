# -*- coding: utf-8 -*-
from odoo import models, fields


class SyncableUnitsMapping(models.Model):
    _name = 'syncable.units.mapping'
    _description = "Units allowed to Sync mapped to Odoo Unit of Measures"

    name = fields.Char(string="Unit Name", required=True)
    unit_of_measure = fields.Many2one('product.uom', string="Unit of measure")
