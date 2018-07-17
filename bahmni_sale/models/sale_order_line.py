# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class SaleOrderLine(models.Model):
    _name = 'sale.order.line'

    external_id = fields.Char(string="External ID",
                              help="This field is used to store encounter ID of bahmni api call")
    external_order_id = fields.Char(string="External Order ID",
                                    help="This field stores the order ID got from api call.")
    order_uuid = fields.Char(string="Order UUID",
                             help="Field for generating a random unique ID.")
    dispensed = fields.Boolean(string="Dispensed",
                               help="Flag to identify whether drug order is dispensed or not.")
    batch_id = fields.Many2one('stock.production.lot', string="Batch No")
    expiry_date = fields.Datetime(string="Expiry date")
    
    @api.model
    def get_available_batch_details(self, product_id, sale_order):
        context = self._context.copy() or {}
        context['location_id'] = sale_order.location_id.id
        context['search_in_child'] = True
        stock_prod_lot = self.pool.get('stock.production.lot')

        already_used_batch_ids = []
        for line in sale_order.order_line:
            if line.batch_id:
                id = line.batch_id.id
                already_used_batch_ids.append(id.__str__())

        query = ['&', ('product_id', '=', product_id), 
                 ('id', 'not in', already_used_batch_ids)]\
                if len(already_used_batch_ids) > 0 else [('product_id','=',product_id)]
        for prodlot in stock_prod_lot.with_context(context).search(query):
            if(prodlot.life_date and datetime.strptime(prodlot.life_date, DTF) >= datetime.today() and prodlot.future_stock_forecast > 0):
                return prodlot
        return None
