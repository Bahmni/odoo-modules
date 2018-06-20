# -*- coding: utf-8 -*-
from odoo import fields, models


class AccountVoucher(models.Model):
    _inherit = 'account.voucher'

    def _calculate_balances(self, cr, uid, ids, name, args, context=None):
        res = {}
        for voucher in self.browse(cr, uid, ids, context=context):
            res[voucher.id] = {'invoice_id': 0,
                               'bill_amount': 0.0}
            line_ids = sorted(voucher.line_ids, key=lambda v: v.id,reverse=True)
            invoice = None
            for voucher_line in line_ids:
                if(voucher_line.type == 'cr'):
                    inv_no = voucher_line.name
                    inv_ids = self.pool.get("account.invoice").search(cr, uid, [('number', '=', inv_no)])
                    if(inv_ids and len(inv_ids) > 0):
                        inv_id = inv_ids[0]
                        invoice = self.pool.get("account.invoice").browse(cr,uid,inv_id,context=context)
                    break
            if(invoice):
                voucher.invoice_id = invoice.id
                res[voucher.id]['bill_amount'] =   invoice.amount_total
                self.write(cr, uid, voucher.id, {'invoice_id': invoice.id})

            if(voucher.state != 'posted'):
                res[voucher.id]['balance_before_pay'] =  self._get_balance_amount(cr,uid,ids,None,None,context)
                res[voucher.id]['balance_amount'] =   self._get_balance_amount(cr,uid,ids,None,None,context) - voucher.amount
                self.write(cr, uid, voucher.id, {'balance_before_pay': res[voucher.id]['balance_before_pay']})
                self.write(cr, uid, voucher.id, {'balance_amount': res[voucher.id]['balance_amount']})

            # if(voucher.state == 'posted'):
            #     #wierd workaround to throw validation error the first time. openerp doesnt support non-blocking messages unless its in on_change
            #     validation_counter()
            #     counter = validation_counter.counter
            #     if(counter%2 !=0):
            #         validation_counter.counter
            #         raise osv.except_osv(_('Warning!'), _('Amount Paid is 0. Do you want to continue?'))

        return res

    balance_before_pay = fields.Float(string="Balance before pay")
    total_balance = fields.Float(string="Total Balance")
    invoice_id = fields.Many2one('account.invoice', string='Invoice')
    bill_amount = fields.Float(string="Bill Amount")
