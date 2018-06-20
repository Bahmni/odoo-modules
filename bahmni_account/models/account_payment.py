# -*- coding: utf-8 -*-
from odoo import models, fields, api


class AccountPayment(models.Model):
    _name = 'account.payment'

    invoice_id = fields.Many2one('account.invoice', string="Invoice")

