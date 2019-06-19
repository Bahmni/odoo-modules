# -*- coding: utf-8 -*-
from odoo import fields, models, api
import logging
_logger = logging.getLogger(__name__)

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'

#     # overridden this method to deduct discounted amount from total of invoice
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 
                 'currency_id', 'company_id', 'date_invoice', 'type', 'discount')
    def _compute_amount(self):
        round_curr = self.currency_id.round
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(round_curr(line.amount) for line in self.tax_line_ids)
        amount_total = self.amount_untaxed + self.amount_tax - self.discount
        self.round_off_amount = self.env['rounding.off'].round_off_value_to_nearest(amount_total)
        self.amount_total = self.amount_untaxed + self.amount_tax - self.discount + self.round_off_amount
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    discount_type = fields.Selection([('none', 'No Discount'),
                                      ('fixed', 'Fixed'),
                                      ('percentage', 'Percentage')],
                                     string="Discount Method",
                                     default='none')
    discount = fields.Monetary(string="Discount")
    discount_percentage = fields.Float(string="Discount Percentage")
    disc_acc_id = fields.Many2one('account.account',
                                  string="Discount Account Head")
    round_off_amount = fields.Monetary(string="Round Off Amount",
                                       compute=_compute_amount)

    @api.onchange('invoice_line_ids')
    def onchange_invoice_lines(self):
        amount_total = self.amount_untaxed + self.amount_tax
        if self.discount_type == 'fixed':
            self.discount_percentage = (self.discount / amount_total) * 100
        elif self.discount_type == 'percentage':
            self.discount = amount_total * self.discount_percentage / 100

    @api.onchange('discount', 'discount_percentage', 'discount_type')
    def onchange_discount(self):
        amount_total = self.amount_untaxed + self.amount_tax
        if self.discount:
            self.discount_percentage = (self.discount / amount_total) * 100
        if self.discount_percentage:
            self.discount = amount_total * self.discount_percentage / 100
            
    @api.model
    def create(self, vals):
        rec = super(AccountInvoice,self).create(vals)
        if rec.origin and self.env.ref('bahmni_account.validate_picking_basedon_invoice').value == '1':
            sale_order = self.env['sale.order'].search([('name','=',rec.origin)])
            if any(sale_order) and len(sale_order.picking_ids):
                for picking in sale_order.picking_ids:
                    picking.force_assign()#Force Available
                    if any(picking.pack_operation_product_ids.filtered(lambda l:l.product_id.tracking != 'none')):
                        _logger.info("\n\n\n*******One of product's configuration is set as Tracking with Unique Serial no or Lots so can't validate this %s Delivery Order.",picking.name)
                        return rec
                    for pack in picking.pack_operation_product_ids:
                        pack.qty_done = pack.product_qty
                    picking.do_new_transfer()#Validate
        return rec
