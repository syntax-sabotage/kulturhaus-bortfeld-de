# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    # SEPA Configuration
    sepa_creditor_identifier = fields.Char(
        string='SEPA Creditor Identifier',
        config_parameter='kulturhaus_membership_sepa.sepa_creditor_id',
        help='Your SEPA creditor identifier for direct debits'
    )
    
    sepa_creditor_name = fields.Char(
        string='Creditor Name',
        config_parameter='kulturhaus_membership_sepa.sepa_creditor_name',
        default='Kulturhaus Bortfeld e.V.',
        help='Name of the creditor organization'
    )
    
    sepa_creditor_iban = fields.Char(
        string='Creditor IBAN',
        config_parameter='kulturhaus_membership_sepa.sepa_creditor_iban',
        help='IBAN of the creditor bank account'
    )
    
    sepa_creditor_bic = fields.Char(
        string='Creditor BIC',
        config_parameter='kulturhaus_membership_sepa.sepa_creditor_bic',
        help='BIC of the creditor bank'
    )
    
    # Membership Period Configuration
    membership_full_year_start = fields.Selection([
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
    ], string='Full Year Collection Month',
       config_parameter='kulturhaus_membership_sepa.full_year_month',
       default='1',
       help='Month when full year memberships are collected')
    
    membership_half_year_start = fields.Selection([
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
    ], string='Half Year Collection Month',
       config_parameter='kulturhaus_membership_sepa.half_year_month',
       default='9',
       help='Month when half year memberships are collected')
    
    membership_half_year_cutoff = fields.Selection([
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
    ], string='Half Year Cutoff Month',
       config_parameter='kulturhaus_membership_sepa.cutoff_month',
       default='7',
       help='Members joining after this month pay half price')
    
    # Pre-notification settings
    sepa_prenotification_days = fields.Integer(
        string='Pre-notification Days',
        config_parameter='kulturhaus_membership_sepa.prenotification_days',
        default=14,
        help='Days before SEPA collection to notify members'
    )
    
    sepa_batch_reference_prefix = fields.Char(
        string='Batch Reference Prefix',
        config_parameter='kulturhaus_membership_sepa.batch_prefix',
        default='KH-SEPA',
        help='Prefix for SEPA batch references'
    )