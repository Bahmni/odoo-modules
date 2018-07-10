# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import fields, models, api


class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    @api.multi
    def name_get(self):
        '''name_get method is overridden to view expiry date in many2one field of lot'''
        if self._context is None:
            context = {}
        else:
            context = self._context.copy()
        res = []
        for record in self:
            name = record.name
            if(record.life_date):
                expiry_date = datetime.strptime(record.life_date, '%Y-%m-%d %H:%M:%S')
                expiry = expiry_date.strftime("%b %d,%Y")
                name = "%s [%s]" % (name, expiry)
            if(context.get('show_future_forcast', False)):
                name = "%s %s" % (name, record.future_stock_forecast)
            res.append((record.id, name))
        return res
    
    sale_price = fields.Float(string="Sale Price")
    mrp = fields.Float(string="MRP")
    cost_price = fields.Float(string="Cost Price")
#     future_stock_forecast = fields.Float(compute=_get_future_stock_forecast)
    