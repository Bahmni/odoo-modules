# -*- coding: utf-8 -*-
from odoo import fields, models


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def _create_lots_for_picking(self):
            Lot = self.env['stock.production.lot']
            for pack_op_lot in self.mapped('pack_operation_ids').mapped('pack_lot_ids'):
                if not pack_op_lot.lot_id:
                    lot = Lot.create({'name': pack_op_lot.lot_name, 
                                      'product_id': pack_op_lot.operation_id.product_id.id,
                                      'life_date': pack_op_lot.expiry_date,
                                      'cost_price': pack_op_lot.cost_price,
                                      'sale_price': pack_op_lot.sale_price,
                                      'mrp': pack_op_lot.mrp})
                    pack_op_lot.write({'lot_id': lot.id})
            # TDE FIXME: this should not be done here
            self.mapped('pack_operation_ids').mapped('pack_lot_ids').filtered(lambda op_lot: op_lot.qty == 0.0).unlink()