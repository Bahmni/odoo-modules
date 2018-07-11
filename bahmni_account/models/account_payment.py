# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.multi
    @api.depends('partner_id', 'amount')
    def _calculate_balances(self):
        if(self.state != 'posted'):
            partner = self.partner_id
            balance = partner.credit or partner.debit
            self.balance_before_pay = balance
            self.total_balance = balance - self.amount

    @api.onchange('invoice_ids')
    def onchange_partner_id(self):
        if self.invoice_ids:
            bill_amount = 0
            for inv in self.invoice_ids:
                bill_amount += inv.amount_total
            self.bill_amount = bill_amount

    balance_before_pay = fields.Float(compute=_calculate_balances,
                                      string="Balance before pay")
    total_balance = fields.Float(compute=_calculate_balances,
                                 string="Total Balance")
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    bill_amount = fields.Float(string="Bill Amount")


