# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    stripe_payment_intent_id = fields.Char(
        string='Stripe Payment Intent',
        help='Stripe Payment Intent ID für automatische Abstimmung'
    )
    
    sepa_batch_id = fields.Many2one(
        'sepa.batch',
        string='SEPA Batch',
        help='Verknüpfte SEPA Batch für Lastschriften'
    )
    
    bank_reconciled = fields.Boolean(
        string='Bank abgestimmt',
        compute='_compute_bank_reconciled',
        store=True
    )
    
    @api.depends('line_ids.reconciled', 'payment_state')
    def _compute_bank_reconciled(self):
        for move in self:
            if move.move_type not in ['out_invoice', 'in_invoice', 'out_refund', 'in_refund']:
                move.bank_reconciled = False
                continue
            
            reconcilable_lines = move.line_ids.filtered(
                lambda l: l.account_id.account_type in ['asset_receivable', 'liability_payable']
            )
            move.bank_reconciled = all(line.reconciled for line in reconcilable_lines)