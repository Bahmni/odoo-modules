
from odoo import fields, models, api, _

class order_type_shop_map(models.Model):
    _name = "order.type.shop.map"
    _description = "Order Type to Shop Mapping"

    order_type = fields.Many2one('order.type','Order Type', required=True)
    shop_id = fields.Many2one('sale.shop', 'Shop')
    location_name = fields.Char('Order Location Name')
    local_shop_id = fields.Many2one('sale.shop', 'Local Shop')



