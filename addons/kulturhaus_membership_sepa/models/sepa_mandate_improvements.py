# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import re
from datetime import datetime, timedelta

class SepaMandateImproved(models.Model):
    _name = 'sepa.mandate'
    _description = 'SEPA Mandat'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'signature_date desc'
    
    name = fields.Char(
        string='Mandatsreferenz',
        required=True,
        readonly=True,
        default='Neu',
        copy=False,
        tracking=True
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Partner',
        required=True,
        tracking=True
    )
    
    iban = fields.Char(
        string='IBAN',
        required=True,
        size=34,
        tracking=True
    )
    
    bic = fields.Char(
        string='BIC',
        size=11,
        tracking=True
    )
    
    bank_name = fields.Char(
        string='Bank Name'
    )
    
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('valid', 'Gültig'),
        ('suspended', 'Ausgesetzt'),
        ('cancelled', 'Gekündigt'),
        ('expired', 'Abgelaufen'),
    ], string='Status', default='draft', tracking=True)
    
    signature_date = fields.Date(
        string='Unterschriftsdatum',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    first_debit_date = fields.Date(
        string='Erste Lastschrift',
        tracking=True
    )
    
    last_debit_date = fields.Date(
        string='Letzte Lastschrift',
        compute='_compute_last_debit_date',
        store=True
    )
    
    expiry_date = fields.Date(
        string='Ablaufdatum',
        help='Mandat läuft automatisch ab, wenn 36 Monate keine Lastschrift',
        compute='_compute_expiry_date',
        store=True
    )
    
    mandate_type = fields.Selection([
        ('recurrent', 'Wiederkehrend'),
        ('one_off', 'Einmalig'),
    ], string='Mandatstyp', default='recurrent', required=True)
    
    scheme = fields.Selection([
        ('core', 'CORE'),
        ('b2b', 'B2B'),
    ], string='Schema', default='core', required=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Unternehmen',
        required=True,
        default=lambda self: self.env.company
    )
    
    creditor_identifier = fields.Char(
        string='Gläubiger-ID',
        related='company_id.sepa_creditor_identifier',
        readonly=True
    )
    
    debit_count = fields.Integer(
        string='Anzahl Lastschriften',
        compute='_compute_debit_count'
    )
    
    total_debited = fields.Monetary(
        string='Gesamt eingezogen',
        compute='_compute_total_debited',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    validation_status = fields.Selection([
        ('valid', 'Gültig'),
        ('invalid_iban', 'Ungültige IBAN'),
        ('invalid_bic', 'Ungültiger BIC'),
        ('blacklisted', 'Gesperrt'),
    ], string='Validierungsstatus', compute='_compute_validation_status')
    
    notes = fields.Text(
        string='Notizen'
    )
    
    # Document management
    mandate_document = fields.Binary(
        string='Unterschriebenes Mandat'
    )
    
    mandate_filename = fields.Char(
        string='Dateiname'
    )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Neu') == 'Neu':
                vals['name'] = self._generate_mandate_reference()
        return super().create(vals_list)
    
    def _generate_mandate_reference(self):
        """Generate unique mandate reference"""
        sequence = self.env['ir.sequence'].next_by_code('sepa.mandate') or 'MANDATE'
        partner_ref = self.partner_id.ref or str(self.partner_id.id)
        date_ref = fields.Date.today().strftime('%Y%m%d')
        return f"{sequence}-{partner_ref}-{date_ref}"
    
    @api.depends('last_debit_date')
    def _compute_expiry_date(self):
        for mandate in self:
            if mandate.last_debit_date:
                mandate.expiry_date = mandate.last_debit_date + timedelta(days=36*30)
            elif mandate.signature_date:
                mandate.expiry_date = mandate.signature_date + timedelta(days=36*30)
            else:
                mandate.expiry_date = False
    
    @api.depends('partner_id')
    def _compute_last_debit_date(self):
        for mandate in self:
            # Would need to check actual SEPA batch history
            last_batch = self.env['sepa.batch.line'].search([
                ('mandate_id', '=', mandate.id),
                ('state', '=', 'executed')
            ], order='execution_date desc', limit=1)
            
            mandate.last_debit_date = last_batch.execution_date if last_batch else False
    
    @api.depends('partner_id')
    def _compute_debit_count(self):
        for mandate in self:
            mandate.debit_count = self.env['sepa.batch.line'].search_count([
                ('mandate_id', '=', mandate.id),
                ('state', '=', 'executed')
            ])
    
    @api.depends('partner_id')
    def _compute_total_debited(self):
        for mandate in self:
            lines = self.env['sepa.batch.line'].search([
                ('mandate_id', '=', mandate.id),
                ('state', '=', 'executed')
            ])
            mandate.total_debited = sum(lines.mapped('amount'))
    
    @api.depends('iban', 'bic')
    def _compute_validation_status(self):
        for mandate in self:
            if not mandate.iban:
                mandate.validation_status = False
            elif not self._validate_iban(mandate.iban):
                mandate.validation_status = 'invalid_iban'
            elif mandate.bic and not self._validate_bic(mandate.bic):
                mandate.validation_status = 'invalid_bic'
            else:
                mandate.validation_status = 'valid'
    
    @api.constrains('iban')
    def _check_iban(self):
        for mandate in self:
            if mandate.iban and not self._validate_iban(mandate.iban):
                raise ValidationError(_('Ungültige IBAN: %s') % mandate.iban)
    
    @api.constrains('bic')
    def _check_bic(self):
        for mandate in self:
            if mandate.bic and not self._validate_bic(mandate.bic):
                raise ValidationError(_('Ungültiger BIC: %s') % mandate.bic)
    
    def _validate_iban(self, iban):
        """Validate IBAN format and checksum"""
        if not iban:
            return False
        
        # Remove spaces and convert to uppercase
        iban = iban.replace(' ', '').upper()
        
        # Check length (German IBANs are 22 characters)
        if not re.match(r'^[A-Z]{2}[0-9]{2}[A-Z0-9]+$', iban):
            return False
        
        # Move first 4 chars to end and convert to integers
        rearranged = iban[4:] + iban[:4]
        numeric = ''
        for char in rearranged:
            if char.isdigit():
                numeric += char
            else:
                numeric += str(ord(char) - ord('A') + 10)
        
        # Check modulo 97
        return int(numeric) % 97 == 1
    
    def _validate_bic(self, bic):
        """Validate BIC format"""
        if not bic:
            return True  # BIC is optional
        
        bic = bic.replace(' ', '').upper()
        return bool(re.match(r'^[A-Z]{6}[A-Z0-9]{2}([A-Z0-9]{3})?$', bic))
    
    def action_validate(self):
        """Validate the mandate"""
        self.ensure_one()
        if self.state != 'draft':
            raise ValidationError(_('Nur Entwürfe können validiert werden.'))
        
        if not self.mandate_document:
            raise ValidationError(_('Bitte laden Sie das unterschriebene Mandat hoch.'))
        
        self.state = 'valid'
        self.first_debit_date = fields.Date.today()
    
    def action_suspend(self):
        """Suspend the mandate"""
        self.ensure_one()
        if self.state != 'valid':
            raise ValidationError(_('Nur gültige Mandate können ausgesetzt werden.'))
        
        self.state = 'suspended'
    
    def action_reactivate(self):
        """Reactivate suspended mandate"""
        self.ensure_one()
        if self.state != 'suspended':
            raise ValidationError(_('Nur ausgesetzte Mandate können reaktiviert werden.'))
        
        # Check if not expired
        if self.expiry_date and self.expiry_date < fields.Date.today():
            raise ValidationError(_('Mandat ist abgelaufen und kann nicht reaktiviert werden.'))
        
        self.state = 'valid'
    
    def action_cancel(self):
        """Cancel the mandate"""
        self.ensure_one()
        self.state = 'cancelled'
    
    @api.model
    def _cron_check_expiry(self):
        """Cron job to check and expire old mandates"""
        today = fields.Date.today()
        expired_mandates = self.search([
            ('state', '=', 'valid'),
            ('expiry_date', '<', today)
        ])
        
        for mandate in expired_mandates:
            mandate.state = 'expired'
            mandate.message_post(
                body=_('Mandat automatisch abgelaufen (36 Monate ohne Nutzung)')
            )