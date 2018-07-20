# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF


class StockPackOperation(models.Model):
    _inherit = 'stock.pack.operation'

    available_qty = fields.Integer(string="Available Qty")
    picking_type = fields.Char(string="Operation Type")

    @api.multi
    def save(self):
        '''This method is overridden to restrict user from assigning expired lots'''
        # TDE FIXME: does not seem to be used -> actually, it does
        # TDE FIXME: move me somewhere else, because the return indicated a wizard, in pack op, it is quite strange
        # HINT: 4. How to manage lots of identical products?
        # Create a picking and click on the Mark as TODO button to display the Lot Split icon. A window will pop-up. Click on Add an item and fill in the serial numbers and click on save button
        for pack in self:
            if pack.product_id.tracking != 'none':
                for lot in pack.pack_lot_ids:
                    life_date = datetime.strptime(lot.lot_id.life_date, DTF)
                    if life_date < datetime.today():
                        raise Warning("Lot %s is expired, you can process expired lot!"%(lot.lot_id.name))
                pack.write({'qty_done': sum(pack.pack_lot_ids.mapped('qty'))})
        return {'type': 'ir.actions.act_window_close'}


class StockPackOperationLot(models.Model):
    _inherit = 'stock.pack.operation.lot'

    available_qty = fields.Integer(string="Available Qty")
    
    @api.onchange('lot_id')
    def onchange_lot_id(self):
        if self.lot_id:
            if self.lot_id.life_date:
                lot_life_date = datetime.strptime(self.lot_id.life_date, DTF)
                if lot_life_date < datetime.today():
                    self.expiry_date = self.lot_id.life_date
                    warning = {'name': 'Lot Expired',
                               'message': "This lot is already expired!"}
                    return {'warning': warning}
            self.available_qty = self.env['product.product'].with_context({'location': self.operation_id.location_id.id,
                                                                           'lot_id': self.lot_id.id}).browse(self.operation_id.product_id.id).qty_available
            self.expiry_date = self.lot_id.life_date
            
