# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    stripe_secret_key = fields.Char(
        string='Stripe Secret Key',
        config_parameter='kulturhaus_stripe_reconcile.stripe_secret_key'
    )
    
    stripe_webhook_secret = fields.Char(
        string='Stripe Webhook Secret',
        config_parameter='kulturhaus_stripe_reconcile.stripe_webhook_secret'
    )
    
    stripe_auto_reconcile = fields.Boolean(
        string='Automatische Abstimmung',
        config_parameter='kulturhaus_stripe_reconcile.auto_reconcile',
        default=True
    )
    
    stripe_fee_account_id = fields.Many2one(
        'account.account',
        string='Gebührenkonto',
        config_parameter='kulturhaus_stripe_reconcile.fee_account_id'
    )