# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime, timedelta

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    # SEPA Mandate Fields
    sepa_mandate_id = fields.Char(
        string='SEPA Mandate ID',
        help='Unique identifier for the SEPA mandate',
        copy=False
    )
    
    sepa_mandate_date = fields.Date(
        string='SEPA Mandate Date',
        help='Date when the SEPA mandate was signed'
    )
    
    sepa_mandate_state = fields.Selection([
        ('draft', 'Draft'),
        ('valid', 'Valid'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled')
    ], string='Mandate State', default='draft', tracking=True)
    
    bank_account_iban = fields.Char(
        string='IBAN',
        size=34,
        help='International Bank Account Number'
    )
    
    bank_account_bic = fields.Char(
        string='BIC',
        size=11,
        help='Bank Identifier Code'
    )
    
    bank_account_holder = fields.Char(
        string='Account Holder',
        help='Name of the bank account holder if different from member'
    )
    
    sepa_last_debit_date = fields.Date(
        string='Last SEPA Debit Date',
        readonly=True,
        help='Date of the last successful SEPA debit'
    )
    
    membership_payment_method = fields.Selection([
        ('sepa', 'SEPA Lastschrift'),
        ('transfer', 'Bank Transfer'),
        ('cash', 'Cash')
    ], string='Payment Method', default='sepa')
    
    # Membership period preference
    membership_period_preference = fields.Selection([
        ('full_year', 'Full Year'),
        ('half_year', 'Half Year'),
        ('auto', 'Automatic (based on join date)')
    ], string='Membership Period', default='auto',
       help='Preference for membership billing period')
    
    @api.model
    def create(self, vals):
        """Generate SEPA mandate ID on creation if SEPA fields are filled"""
        partner = super().create(vals)
        if partner.bank_account_iban and not partner.sepa_mandate_id:
            partner.sepa_mandate_id = self._generate_mandate_id()
            if partner.sepa_mandate_state == 'draft':
                partner.sepa_mandate_state = 'valid'
        return partner
    
    def _generate_mandate_id(self):
        """Generate unique SEPA mandate ID"""
        sequence = self.env['ir.sequence'].next_by_code('sepa.mandate') or 'SEPA'
        return f"KH-{sequence}-{datetime.now().strftime('%Y%m')}"
    
    @api.depends('bank_account_iban')
    def _compute_display_name(self):
        """Add SEPA indicator to display name if has valid mandate"""
        super()._compute_display_name()
        for partner in self:
            if partner.sepa_mandate_state == 'valid':
                partner.display_name = f"{partner.display_name} [SEPA]"
    
    def action_validate_mandate(self):
        """Action to validate SEPA mandate"""
        self.ensure_one()
        if self.bank_account_iban:
            if not self.sepa_mandate_id:
                self.sepa_mandate_id = self._generate_mandate_id()
            self.sepa_mandate_state = 'valid'
            self.sepa_mandate_date = fields.Date.today()
    
    def action_cancel_mandate(self):
        """Action to cancel SEPA mandate"""
        self.ensure_one()
        self.sepa_mandate_state = 'cancelled'
    
    @api.model
    def get_sepa_eligible_members(self, period='full_year'):
        """Get members eligible for SEPA batch"""
        domain = [
            ('membership_state', 'in', ['waiting', 'invoiced', 'paid']),
            ('sepa_mandate_state', '=', 'valid'),
            ('bank_account_iban', '!=', False)
        ]
        
        if period == 'half_year':
            # Members who joined after June
            current_year = datetime.now().year
            domain.append(('membership_start', '>=', f'{current_year}-07-01'))
        
        return self.search(domain)