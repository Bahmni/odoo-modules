# -*- coding: utf-8 -*-
from odoo import fields, models, api


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

    @api.onchange('discount_percentage', 'invoice_line_ids')
    def onchange_discount_percentage(self):
        if self.discount_percentage:
            amount_total = self.amount_untaxed + self.amount_tax
            if self.discount_type == 'percentage':
                discount = (amount_total * self.discount_percentage) / 100
                self.discount = discount

#     @api.onchange('discount_type')
#     def onchange_discount_type(self):
#         '''Method to set values of fields to zero, when
#         those are  not considerable in calculation'''
#         self.discount_percentage = 0
#         self.discount = 0
