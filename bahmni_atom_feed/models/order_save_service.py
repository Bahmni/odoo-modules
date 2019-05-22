# -*- coding: utf-8 -*-
from datetime import datetime
import json
from itertools import groupby
import logging

from odoo import fields, models, api
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DTF
from odoo.exceptions import Warning

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
    def _get_warehouse_id(self, location, orderType):
        _logger.info("!!!!!!!ORDER TYPE!!!!!!!!!")
        _logger.info(orderType)
        if location:
            order_type = self.env['order.type'].search([('name', '=', orderType)])
            if not order_type:
		order_type = self.env['order.type'].create({'name':orderType})
            operation_types = self.env['stock.picking.type'].search([('default_location_src_id', '=', location.id)])
            if order_type and operation_types:
                mapping = self.env['order.picking.type.mapping'].search([('order_type_id', '=', order_type.id),
                                                                         ('picking_type_id', 'in', operation_types.ids)],
                                                                        limit=1)
                if mapping:
                    warehouse = mapping.picking_type_id.warehouse_id
            elif not order_type and operation_types:
                operation_type = self.env['stock.picking.type'].search([('default_location_src_id', '=', location.id)],
                                                                        limit=1)
                warehouse = operation_type.warehouse_id
            else:
                # either location should exist as stock location of a warehouse.
                warehouse = self.env['stock.warehouse'].search([('lot_stock_id', '=', location.id)])
                if not warehouse:
                    _logger.warning("Location is neither mapped to warehouse nor to any Operation type, hence sale order creation failed!")
                    return
                else:
                    return warehouse.id
        else:
            _logger.warning("Location with name '%s' does not exists in the system")

       
    @api.model 
    def _get_shop_and_local_shop_id(self, orderType, location_name):
        _logger.info("\n\n _get_shop_and_local_shop_id().... Called.....")
        _logger.info("orderType %s",orderType)
        _logger.info("location_name %s",location_name)
        OrderTypeShopMap = self.env['order.type.shop.map']
        SaleShop = self.env['sale.shop']
        if (location_name):
            order_type_rocord = self.env['order.type'].search([('name','=',orderType)])
            _logger.info("\n\n*****order_type_rocord=%s",order_type_rocord)			
            shop_list_with_orderType = OrderTypeShopMap.search([('order_type', '=', order_type_rocord.id), ('location_name', '=', location_name)])
            _logger.info("shop_list_with_orderType %s",shop_list_with_orderType)
            if not shop_list_with_orderType:
                shop_list_with_orderType = OrderTypeShopMap.search([('order_type', '=', order_type_rocord.id), ('location_name', '=', 	None)])
                _logger.info(" if not shop_list_with_orderType %s",shop_list_with_orderType)
                if not shop_list_with_orderType:
                    return (False, False)
            _logger.info("Final.....shop_list_with_orderType %s", shop_list_with_orderType)
            order_type_map_object = shop_list_with_orderType[0]
            if order_type_map_object.shop_id:
                shop_id = order_type_map_object.shop_id.id
            else:
                shop_records = SaleShop.search([])
                first_shop = shop_records[0]
                shop_id = first_shop.id

            if order_type_map_object.local_shop_id:
                local_shop_id = order_type_map_object.local_shop_id.id
            else:
                local_shop_id = False
            return (shop_id, local_shop_id)
        return (False, False)



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
                # will return order line data for products which exists in the system, either with productID passed or with conceptName
                unprocessed_orders = self._filter_processed_orders(orders)
                tup = self._get_shop_and_local_shop_id(orderType, location_name)
                shop_id = tup[0]
                local_shop_id = tup[1]

                if (not shop_id):
                    continue
                # instead of shop_id, warehouse_id is needed.
                # in case of odoo 10, warehouse_id is required for creating order, not shop
                # with each stock_picking_type, a warehouse id is linked.
                # with each stock picking type, there exists a source_location and destination_location
                # hence, creating a new object for ordertype and stock_picking_type mapping
                # if mapping record with passed orderType does not exists, 
                # will search for picking type whose source location is same as passed location, and it's linked warehouse will get passed to the order.
                # else will look for warehouse, whose stock location is as per the location name
                # without warehouse id, order cannot be created
                location = self.env['stock.location'].search([('name', '=', location_name)], limit=1)
                if not location:
                   location = self.env['stock.location'].create({'name':location_name})
                if not location:
                    _logger.warning("No location found with name: %s"%(location_name))
                warehouse_id = self._get_warehouse_id(location, orderType)
                if not warehouse_id:
                    #self.env['stock.warehouse'].create({'name':,'code':})
                    operation_type = self.env['stock.picking.type'].search([('name', '=', 'Delivery Orders')],
                                                                        limit=1)
                    warehouse_id = operation_type.warehouse_id.id
                _logger.info("!!!!!!!!!!!!!!!WAREHOUSE!!!!!!!!!!!!!!!!!!!!!")
                _logger.info(warehouse_id)

                name = self.env['ir.sequence'].next_by_code('sale.order')
                #Adding both the ids to the unprocessed array of orders, Separating to dispensed and non-dispensed orders
                unprocessed_dispensed_order = []
                unprocessed_non_dispensed_order = []
                for unprocessed_order in unprocessed_orders:
                    unprocessed_order['location_id'] = location.id
                    unprocessed_order['warehouse_id'] = warehouse_id
                    if(unprocessed_order.get('dispensed', 'false') == 'true'):
                        unprocessed_dispensed_order.append(unprocessed_order)
                    else:
                        unprocessed_non_dispensed_order.append(unprocessed_order)

                if(len(unprocessed_non_dispensed_order) > 0):
                    sale_order_ids = self.env['sale.order'].search([('partner_id', '=', cus_id.id),
                                                                    ('location_id', '=', unprocessed_non_dispensed_order[0]['location_id']),
                                                                    ('state', '=', 'draft'),
                                                                    ('origin', '=', 'ATOMFEED SYNC')])

                    if(not sale_order_ids):
                        dispensed = False
                        if unprocessed_order.get('dispensed') == 'true':
                            dispensed = True
                        # Non Dispensed New
                        # replaced create_sale_order method call
                        sale_order_vals = {'partner_id': cus_id.id,
                                           'location_id': unprocessed_non_dispensed_order[0]['location_id'],
                                           'warehouse_id': unprocessed_non_dispensed_order[0]['warehouse_id'],
                                           'care_setting': care_setting,
                                           'provider_name': provider_name,
                                           'date_order': datetime.strftime(datetime.now(), DTF),
                                           'pricelist_id': cus_id.property_product_pricelist and cus_id.property_product_pricelist.id or False,
                                           'picking_policy': 'direct',
                                           'state': 'draft',
                                           'dispensed': dispensed,
                                           'shop_id' : shop_id,
                                           'origin' : 'ATOMFEED SYNC',
                                           }
                        sale_order = self.env['sale.order'].create(sale_order_vals)
                        for rec in unprocessed_non_dispensed_order:
                            self._process_orders(sale_order, unprocessed_non_dispensed_order, rec)
                    else:
                        # Non Dispensed Update
                        # replaced update_sale_order method call
                        for order in sale_order_ids:
                            order.write({'care_setting': care_setting,
                                         'provider_name': provider_name})
                            if order.state != 'draft':
                                _logger.error("Sale order for patient : %s is already approved"%(cus_id.name))
                            else:
                                for rec in unprocessed_non_dispensed_order:
                                    self._process_orders(order, unprocessed_non_dispensed_order, rec)

                    sale_order_ids_for_dispensed = self.env['sale.order'].search([('partner_id', '=', cus_id.id),
                                                                                  ('location_id', '=', unprocessed_non_dispensed_order[0]['location_id']),
                                                                                  ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC'),('dispensed','=',True)])

                    if(len(sale_order_ids_for_dispensed) > 0):
                        if(sale_order_ids_for_dispensed[0]):
                            sale_order_line_ids_for_dispensed = self.env['sale.order.line'].search([('order_id', '=', sale_order_ids_for_dispensed[0])])
                            if(len(sale_order_line_ids_for_dispensed) != 0):
                                for so_ids in sale_order_line_ids_for_dispensed:
                                    so_ids.unlink()


                if(len(unprocessed_dispensed_order) > 0 and location) :
                    sale_order_ids = self.env['sale.order'].search([('partner_id', '=', cus_id),
                                                                    ('location_id', '=', unprocessed_dispensed_order[0]['location_id']),
                                                                    ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')])

                    sale_order_ids_for_dispensed = self.env['sale.order'].search([('partner_id', '=', cus_id),
                                                                                  ('location_id', '=', unprocessed_dispensed_order[0]['location_id']),
                                                                                  ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC'),('dispensed','=',True)])

                    if(not sale_order_ids_for_dispensed):
                        #Remove existing sale order line
                        self._remove_existing_sale_order_line(sale_order_ids[0],unprocessed_dispensed_order)

                        #Removing existing empty sale order
                        sale_order_line_ids = self.env['sale.order.line'].search([('order_id', '=', sale_order_ids[0])])

                        if(len(sale_order_line_ids) == 0):
                            sale_order_ids.unlink()

                        #Dispensed New

                        sale_order_vals = {'partner_id': cus_id.id,
                                           'location_id': unprocessed_non_dispensed_order[0]['location_id'],
                                           'warehouse_id': unprocessed_non_dispensed_order[0]['warehouse_id'],
                                           'care_setting': care_setting,
                                           'provider_name': provider_name,
                                           'date_order': datetime.strftime(datetime.now(), DTF),
                                           'pricelist_id': cus_id.property_product_pricelist and cus_id.property_product_pricelist.id or False,
                                           'picking_policy': 'direct',
                                           'state': 'draft',
                                           'dispensed': dispensed,
                                           'shop_id' : shop_id,
                                           'origin' : 'ATOMFEED SYNC',
                                           }

                        sale_order = self.env['sale.order'].create(sale_order_vals)


                        #self._create_sale_order(cus_id, name, unprocessed_dispensed_order[0]['location_id'],
                        #unprocessed_dispensed_order, care_setting, provider_name)
# 
#                         if(self._allow_automatic_convertion_to_saleorder(cr,uid)):
#                             sale_order_ids_for_dispensed = self.pool.get('sale.order').search(cr, uid, [('partner_id', '=', cus_id), ('shop_id', '=', unprocessed_dispensed_order[0]['custom_local_shop_id']), ('state', '=', 'draft'), ('origin', '=', 'ATOMFEED SYNC')], context=context)
#                             self.pool.get('sale.order').action_button_confirm(cr, uid, sale_order_ids_for_dispensed, context)

                    else:
                        #Remove existing sale order line
                        self._remove_existing_sale_order_line(sale_order_ids[0],unprocessed_dispensed_order)

                        #Removing existing empty sale order
                        sale_order_line_ids = self.env['sale.order.line'].search([('order_id', '=', sale_order_ids[0])])
                        if(len(sale_order_line_ids) == 0):
                            sale_order_ids.unlink()

                        #Dispensed Update
                        self._update_sale_order(cus_id, name, unprocessed_dispensed_order[0]['location'], care_setting, sale_order_ids_for_dispensed[0], unprocessed_dispensed_order, provider_name)
        else:
            raise Warning("Patient Id not found in openerp")

    @api.model
    def _remove_existing_sale_order_line(self, sale_order_id, unprocessed_dispensed_order):
        sale_order_lines = self.env['sale.order.line'].search([('order_id', '=', sale_order_id)])
        sale_order_lines_to_be_saved = []
        for order in unprocessed_dispensed_order:
            for sale_order_line in sale_order_lines:
                if(order['orderId'] == sale_order_line.external_order_id):
                    if order.get('dispensed')=='false':
                        dispensed_status = False
                    else:
                        dispensed_status = True
                    if(dispensed_status != sale_order_line.dispensed_status):
                        sale_order_lines_to_be_saved.append(sale_order_line)

        for rec in sale_order_lines_to_be_saved:
            rec.unlink()
        
    @api.model
    def _process_orders(self, sale_order, all_orders, order):

        order_in_db = self.env['sale.order.line'].search([('external_order_id', '=', order['orderId'])])

        if(order_in_db or self._order_already_processed(order['orderId'], order.get('dispensed', False))):
            return

        parent_order_line = []
        # if(order.get('previousOrderId', False) and order.get('dispensed', "") == "true"):
        #     self._create_sale_order_line(cr, uid, name, sale_order, order, context)

        if(order.get('previousOrderId', False) and order.get('dispensed', "") == "false"):
            parent_order = self._fetch_parent(all_orders, order)
            if(parent_order):
                self._process_orders(sale_order, all_orders, parent_order)
            parent_order_line = self.env['sale.order.line'].search([('external_order_id', '=', order['previousOrderId'])])
            if(not parent_order_line and not self._order_already_processed(order['previousOrderId'], order.get('dispensed', False))):
                raise Warning("Previous order id does not exist in DB. This can be because of previous failed events")

        if(order["voided"] or order.get('action', "") == "DISCONTINUE"):
            self._delete_sale_order_line(parent_order_line)
        elif(order.get('action', "") == "REVISE" and order.get('dispensed', "") == "false"):
            self._update_sale_order_line(sale_order.id, order, parent_order_line)
        else:
            self._create_sale_order_line(sale_order.id, order)
    
    @api.model
    def _delete_sale_order_line(self, parent_order_line):
        if(parent_order_line):
            if(parent_order_line[0] and parent_order_line[0].order_id.state == 'draft'):
                for parent in parent_order_line:
                    parent.unlink()
    
    @api.model
    def _update_sale_order_line(self, sale_order, order, parent_order_line):
        self._delete_sale_order_line(parent_order_line)
        self._create_sale_order_line(sale_order, order)
    
    @api.model
    def _create_sale_order_line(self, sale_order, order):
        if(self._order_already_processed(order['orderId'],order.get('dispensed', False))):
            return
        self._create_sale_order_line_function(sale_order, order)
        
    @api.model
    def _get_order_quantity(self, order, default_quantity_value):
        if(not self.env['syncable.units'].search([('name', '=', order['quantityUnits'])])):
            return default_quantity_value
        return order['quantity']
    
    @api.model
    def _create_sale_order_line_function(self, sale_order, order):
        stored_prod_ids = self._get_product_ids(order)

        if(stored_prod_ids):
            prod_id = stored_prod_ids[0]
            prod_obj = self.env['product.product'].browse(prod_id)
            sale_order_line_obj = self.env['sale.order.line']
            prod_lot = sale_order_line_obj.get_available_batch_details(prod_id, sale_order)

            actual_quantity = order['quantity']
            comments = " ".join([str(actual_quantity), str(order.get('quantityUnits', None))])

            default_quantity_total = self.env.ref('bahmni_sale.group_default_quantity')
            _logger.info("DEFAULT QUANTITY TOTAL")
            _logger.info(default_quantity_total)
            default_quantity_value = 1
            if default_quantity_total and len(default_quantity_total.users) > 0:
                default_quantity_value = -1

            order['quantity'] = self._get_order_quantity(order, default_quantity_value)
            product_uom_qty = order['quantity']
            if(prod_lot != None and order['quantity'] > prod_lot.future_stock_forecast):
                product_uom_qty = prod_lot.future_stock_forecast

            sale_order_line = {
                'product_id': prod_id,
                'price_unit': prod_obj.list_price,
                'comments': comments,
                'product_uom_qty': product_uom_qty,
                'product_uom': prod_obj.uom_id.id,
                'order_id': sale_order,
                'external_id':order['encounterId'],
                'external_order_id':order['orderId'],
                'name': prod_obj.name,
                'type': 'make_to_stock',
                'state': 'draft',
                'dispensed': True if order.get('dispensed') == 'true' or (order.get('dispensed') and order.get('dispensed')!='false') else False
            }

            if prod_lot != None:
                life_date = prod_lot.life_date and datetime.strptime(prod_lot.life_date, DTF)
                sale_order_line['price_unit'] = prod_lot.sale_price if prod_lot.sale_price > 0.0 else sale_order_line['price_unit']
                sale_order_line['batch_name'] = prod_lot.name
                sale_order_line['batch_id'] = prod_lot.id
                sale_order_line['expiry_date'] = life_date and life_date.strftime('%d/%m/%Y')

            sale_order_line_obj.create(sale_order_line)

            sale_order = self.env['sale.order'].browse(sale_order)

            if product_uom_qty != order['quantity']:
                order['quantity'] = order['quantity'] - product_uom_qty
                self._create_sale_order_line_function(sale_order, order)
    
    def _fetch_parent(self, all_orders, child_order):
        for order in all_orders:
            if(order.get("orderId") == child_order.get("previousOrderId")):
                return order

    @api.model
    def _filter_processed_orders(self, orders):
        unprocessed_orders = []
        dispensed_status = False

        for order in orders:
            if order.get('dispensed') == 'true':
                dispensed_status = True
            else:
                dispensed_status = False
            if (not self._order_already_processed(order['orderId'], dispensed_status)):
                unprocessed_orders.append(order)
        return self._filter_products_undefined(unprocessed_orders)

    @api.model
    def _order_already_processed(self, OrderID, Dstatus):
        processed_drug_order_id = self.env['sale.order.line'].search([('external_order_id', '=', OrderID), ('dispensed', '=', Dstatus)])
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
    
