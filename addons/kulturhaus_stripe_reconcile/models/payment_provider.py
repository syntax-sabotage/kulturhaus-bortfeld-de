# -*- coding: utf-8 -*-
from odoo import models, fields

class PaymentProvider(models.Model):
    _inherit = 'payment.provider'
    
    stripe_webhook_configured = fields.Boolean(
        string='Webhook Konfiguriert',
        default=False
    )