# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    stripe_payment_ids = fields.One2many(
        'stripe.payment',
        'move_id',
        string='Stripe Zahlungen'
    )
    
    stripe_payment_count = fields.Integer(
        string='Stripe Zahlungen',
        compute='_compute_stripe_payment_count'
    )
    
    has_stripe_payment = fields.Boolean(
        string='Hat Stripe Zahlung',
        compute='_compute_has_stripe_payment',
        store=True
    )
    
    @api.depends('stripe_payment_ids')
    def _compute_stripe_payment_count(self):
        for move in self:
            move.stripe_payment_count = len(move.stripe_payment_ids)
    
    @api.depends('stripe_payment_ids')
    def _compute_has_stripe_payment(self):
        for move in self:
            move.has_stripe_payment = bool(move.stripe_payment_ids)
    
    def action_view_stripe_payments(self):
        """View related Stripe payments"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Stripe Zahlungen',
            'res_model': 'stripe.payment',
            'view_mode': 'list,form',
            'domain': [('move_id', '=', self.id)],
            'context': {'default_move_id': self.id},
        }