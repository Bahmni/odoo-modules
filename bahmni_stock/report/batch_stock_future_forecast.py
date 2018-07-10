# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import Warning
from odoo.tools import drop_view_if_exists


class BatchStockFutureForecast(models.Model):
    _name = 'batch.stock.future.forecast'
    _description = "Stock report by batch number considering future availabilty"
    _auto = False

    qty = fields.Float(string="Quantity")
    location_id = fields.Many2one('stock.location', string="Location")
    product_id = fields.Many2one('product.product', string="Product")
    lot_id = fields.Many2one('stock.production.lot', string="Lot")

    @api.model_cr
    def init(self):
        drop_view_if_exists(self.env.cr, 'batch_stock_future_forecast')
        self.env.cr.execute("""
            create or replace view batch_stock_future_forecast as (
                select max(id) as id,
                    location_id,
                    product_id,
                    lot_id,
                    round(sum(qty),3) as qty
                from (
                    select -max(sm.id) as id,
                        sm.location_id,
                        sm.product_id,
                        sq.lot_id,
                        -sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_quant_move_rel as sqmr 
                        on (stock_quant_move_rel.move_id=sm.id)
                    left join stock_quant as sq
                        on (stock_quant_move_rel.quant_id=sq.id)
                    left join stock_location sl
                        on (sl.id = sm.location_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    where sm.state in ('done', 'confirmed')
                    group by sm.location_id, sm.product_id, sm.product_uom, sq.lot_id
                    union all
                    select max(sm.id) as id,
                        sm.location_dest_id as location_id,
                        sm.product_id,
                        sq.lot_id,
                        sum(sm.product_qty /uo.factor) as qty
                    from stock_move as sm
                    left join stock_quant_move_rel as sqmr
                        on (stock_quant_move_rel.move_id = sm.id)
                    left join stock_quant as sq 
                        on (stock_quant_move_rel.quant_id = sq.id)
                    left join stock_location sl
                        on (sl.id = sm.location_dest_id)
                    left join product_uom uo
                        on (uo.id=sm.product_uom)
                    where sm.state in ('done', 'confirmed')
                    group by sm.location_dest_id, sm.product_id, sm.product_uom, sq.lot_id
                ) as report
                group by location_id, product_id, lot_id
            )""")

    @api.multi
    def unlink(self):
        raise Warning('You cannot delete any record!')