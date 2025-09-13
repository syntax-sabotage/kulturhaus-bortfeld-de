# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    is_membership_sepa = fields.Boolean(
        string='SEPA Membership Product',
        help='Check if this product should use SEPA payment by default'
    )
    
    membership_period_type = fields.Selection([
        ('full_year', 'Full Year Membership'),
        ('half_year', 'Half Year Membership'),
        ('custom', 'Custom Period')
    ], string='Membership Period Type')
    
    sepa_batch_month = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ], string='SEPA Collection Month',
       help='Default month for SEPA collection for this product')
    
    force_sepa_payment = fields.Boolean(
        string='Force SEPA Payment',
        help='If checked, only SEPA payment will be allowed for this product'
    )
    
    @api.onchange('membership')
    def _onchange_membership(self):
        """When product is marked as membership, suggest SEPA settings"""
        if self.membership:
            self.is_membership_sepa = True