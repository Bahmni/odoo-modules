# -*- coding: utf-8 -*-
import json
from itertools import groupby
import logging

from odoo import fields, models, api

_logger = logging.getLogger(__name__)


class OrderSaveService(models.Model):
    _name = 'order.save.service'
    _auto = False

    def _get_openerp_orders(self, vals):
        if(not vals.get("orders", None)):
            return None
        orders_string = vals.get("orders")
        order_group = json.loads(orders_string)
        return order_group.get('openERPOrders', None)

    @api.model
    def create_orders(self, vals):
        customer_id = vals.get("customer_id")
        location_name = vals.get("locationName")
        all_orders = self._get_openerp_orders(vals)

        if(not all_orders):
            return ""

        customer_ids = self.env['res.partner'].search([('ref', '=', customer_id)])
        if(customer_ids):
            cus_id = customer_ids[0]

            for orderType, ordersGroup in groupby(all_orders, lambda order: order.get('type')):

                orders = list(ordersGroup)
                care_setting = orders[0].get('visitType').lower()
                provider_name = orders[0].get('providerName')
                unprocessed_orders = self._filter_processed_orders(orders)
# 
#                 tup = self._get_shop_and_local_shop_id(cr, uid, orderType, location_name, context)
#                 shop_id = tup[0]
#                 local_shop_id = tup[1]
                # instead of shop_id, warehouse_id is needed.
                location = self.env['stock.location'].search([('name', '=ilike', location_name)], limit=1)
                if not location:
                    _logger.warning("No location found with name: %s"%(location_name))

                if location:
                    # either location should exist as stock location of a warehouse.
                    warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', location.id)])
                    if not warehouse:
                        # or it should be a child location of stock location of main warehouse in case of single warehouse system.
                        # in this case, child location has to be mapped in a operation type.
                        operation_type = self.env['stock.picking.type'].search([('default_location_src_id', '=', location.id)],
                                                                               limit=1)
                        if operation_type:
                            warehouse = operation_type.warehouse_id
                    if not warehouse:
                        _logger.warning("Location is neither mapped to warehouse nor to any Operation type, hence sale order creation failed!")
                        return
#                 if(not shop_id):
#                     continue

                name = self.env['ir.sequence'].next_by_code('sale.order')
                #Adding both the ids to the unprocessed array of orders, Separating to dispensed and non-dispensed orders
                unprocessed_dispensed_order = []
                unprocessed_non_dispensed_order = []
                for unprocessed_order in unprocessed_orders:
                    unprocessed_order['location_id'] = location.id
                    unprocessed_order['warehouse_id'] = warehouse.id
                    if(unprocessed_order.get('dispensed', 'false') == 'true'):
                        unprocessed_dispensed_order.append(unprocessed_order)
                    else:
                        unprocessed_non_dispensed_order.append(unprocessed_order)

                if(len(unprocessed_non_dispensed_order) > 0):
                    sale_order_ids = self.env['sale.order'].search([('partner_id', '=', cus_id),
                                                                    ('location_id', '=', unprocessed_non_dispensed_order[0]['location_id']),
                                                                    ('state', '=', 'draft'),
                                                                    ('origin', '=', 'ATOMFEED SYNC')])

                    if(not sale_order_ids):
                        #Non Dispensed New
                        self._create_sale_order(cus_id, name, unprocessed_non_dispensed_order[0]['location_id'], unprocessed_non_dispensed_order, care_setting, provider_name)
                    else:
                        #Non Dispensed Update
                        self._update_sale_order(cus_id, name, unprocessed_non_dispensed_order[0]['location_id'], care_setting, sale_order_ids[0], unprocessed_non_dispensed_order, provider_name, context)

                    sale_order_ids_for_dispensed = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_non_dispensed_order[0]['custom_local_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)

                    if(len(sale_order_ids_for_dispensed) > 0):
                        if(sale_order_ids_for_dispensed[0]) :
                            sale_order_line_ids_for_dispensed = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order_ids_for_dispensed[0])], context=context)
                            if(len(sale_order_line_ids_for_dispensed) == 0):
                                self.pool.get('sale.order').unlink(cr, uid, sale_order_ids_for_dispensed, context=context)


                if(len(unprocessed_dispensed_order) > 0 and local_shop_id) :
                    sale_order_ids = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_dispensed_order[0]['custom_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)

                    sale_order_ids_for_dispensed = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_dispensed_order[0]['custom_local_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)

                    if(not sale_order_ids_for_dispensed):
                        #Remove existing sale order line
                        self._remove_existing_sale_order_line(cr,uid,sale_order_ids[0],unprocessed_dispensed_order,context=context)

                        #Removing existing empty sale order
                        sale_order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order_ids[0])], context=context)

                        if(len(sale_order_line_ids) == 0):
                            self.pool.get('sale.order').unlink(cr, uid, sale_order_ids, context=context)

                        #Dispensed New
                        self._create_sale_order(cr, uid, cus_id, name, unprocessed_dispensed_order[0]['custom_local_shop_id'], unprocessed_dispensed_order, care_setting, provider_name, context)

                        if(self._allow_automatic_convertion_to_saleorder (cr,uid)):
                            sale_order_ids_for_dispensed = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_dispensed_order[0]['custom_local_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)
                            self.pool.get('sale.order').action_button_confirm(cr, uid, sale_order_ids_for_dispensed, context)

                    else:
                        #Remove existing sale order line
                        self._remove_existing_sale_order_line(cr,uid,sale_order_ids[0],unprocessed_dispensed_order,context=context)

                        #Removing existing empty sale order
                        sale_order_line_ids = self.pool.get('sale.order.line').search(cr, uid, [('order_id', '=', sale_order_ids[0])], context=context)
                        if(len(sale_order_line_ids) == 0):
                            self.pool.get('sale.order').unlink(cr, uid, sale_order_ids, context=context)

                        #Dispensed Update
                        self._update_sale_order(cr, uid, cus_id, name, unprocessed_dispensed_order[0]['custom_local_shop_id'], care_setting, sale_order_ids_for_dispensed[0], unprocessed_dispensed_order, provider_name, context)
        else:
            raise osv.except_osv(('Error!'), ("Patient Id not found in openerp"))

    @api.model
    def _filter_processed_orders(self, orders):
        unprocessed_orders = []
        dispensed_status = False

        for order in orders:
            if order.get('dispensed') == 'true':
                dispensed_status = True
            if (not self._order_already_processed(order['orderId'], dispensed_status)):
                unprocessed_orders.append(order)
        return self._filter_products_undefined(unprocessed_orders)

    @api.model
    def _order_already_processed(self, order_uuid, dispensed_status):
        processed_drug_order_id = self.env['sale.order.line'].search([('external_order_id', '=', order_uuid), ('dispensed', '=', dispensed_status)])
        return processed_drug_order_id

    @api.model
    def _filter_products_undefined(self, orders):
        products_in_system = []

        for order in orders:
            stored_prod_ids = self._get_product_ids(order)
            if(stored_prod_ids):
                products_in_system.append(order)
        return products_in_system

    @api.model
    def _get_product_ids(self, order):
        if order['productId']:
            prod_ids = self.env['product.product'].search([('uuid', '=', order['productId'])])
        else:
            prod_ids = self.env['product.product'].search([('name', '=', order['conceptName'])])

        return prod_ids.ids
    
