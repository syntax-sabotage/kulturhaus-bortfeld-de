# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging

_logger = logging.getLogger(__name__)

class SepaAutomaticBatch(models.Model):
    _name = 'sepa.automatic.batch'
    _description = 'Automatische SEPA Batch Generierung'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'next_run_date'
    
    name = fields.Char(
        string='Name',
        required=True
    )
    
    active = fields.Boolean(
        string='Aktiv',
        default=True
    )
    
    batch_type = fields.Selection([
        ('monthly', 'Monatlich'),
        ('quarterly', 'Vierteljährlich'),
        ('half_yearly', 'Halbjährlich'),
        ('yearly', 'Jährlich'),
    ], string='Frequenz', required=True, default='monthly')
    
    next_run_date = fields.Date(
        string='Nächste Ausführung',
        required=True,
        tracking=True
    )
    
    last_run_date = fields.Date(
        string='Letzte Ausführung',
        tracking=True
    )
    
    membership_product_ids = fields.Many2many(
        'product.template',
        string='Mitgliedschaftsprodukte',
        domain=[('membership', '=', True)]
    )
    
    partner_filter = fields.Selection([
        ('all', 'Alle aktiven Mitglieder'),
        ('specific', 'Bestimmte Mitglieder'),
        ('tags', 'Nach Tags'),
    ], string='Mitgliederfilter', default='all')
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='Spezifische Mitglieder'
    )
    
    partner_tag_ids = fields.Many2many(
        'res.partner.category',
        string='Mitglieder-Tags'
    )
    
    amount_type = fields.Selection([
        ('fixed', 'Fester Betrag'),
        ('membership', 'Mitgliedsbeitrag'),
        ('custom', 'Individueller Betrag'),
    ], string='Betragstyp', default='membership')
    
    fixed_amount = fields.Float(
        string='Fester Betrag'
    )
    
    execution_day = fields.Integer(
        string='Ausführungstag',
        default=15,
        help='Tag des Monats für die Ausführung (1-28)'
    )
    
    advance_days = fields.Integer(
        string='Vorlaufzeit (Tage)',
        default=5,
        help='Tage vor Fälligkeit für SEPA Einreichung'
    )
    
    company_id = fields.Many2one(
        'res.company',
        string='Unternehmen',
        required=True,
        default=lambda self: self.env.company
    )
    
    batch_history_ids = fields.One2many(
        'sepa.batch.history',
        'automatic_batch_id',
        string='Batch Historie'
    )
    
    @api.model
    def _cron_generate_batches(self):
        """Cron job to generate SEPA batches automatically"""
        today = fields.Date.today()
        batches = self.search([
            ('active', '=', True),
            ('next_run_date', '<=', today)
        ])
        
        for batch in batches:
            try:
                batch.generate_batch()
            except Exception as e:
                _logger.error(f"Error generating automatic batch {batch.name}: {e}")
                batch.message_post(
                    body=_("Fehler bei automatischer Batch-Generierung: %s") % str(e)
                )
    
    def generate_batch(self):
        """Generate SEPA batch based on configuration"""
        self.ensure_one()
        
        # Get eligible partners
        partners = self._get_eligible_partners()
        
        if not partners:
            self.message_post(body=_("Keine berechtigten Mitglieder für Batch gefunden."))
            return False
        
        # Calculate collection date
        collection_date = self.next_run_date + timedelta(days=self.advance_days)
        
        # Prepare batch data
        batch_lines = []
        for partner in partners:
            # Check for valid mandate
            mandate = partner.sepa_mandate_ids.filtered(
                lambda m: m.state == 'valid'
            )[:1]
            
            if not mandate:
                continue
            
            # Calculate amount
            amount = self._calculate_amount(partner)
            
            if amount <= 0:
                continue
            
            batch_lines.append({
                'partner_id': partner.id,
                'mandate_id': mandate.id,
                'amount': amount,
                'reference': self._get_payment_reference(partner),
            })
        
        if not batch_lines:
            self.message_post(body=_("Keine gültigen SEPA-Mandate gefunden."))
            return False
        
        # Create batch history record
        batch_history = self.env['sepa.batch.history'].create({
            'automatic_batch_id': self.id,
            'batch_date': fields.Date.today(),
            'collection_date': collection_date,
            'total_amount': sum(line['amount'] for line in batch_lines),
            'partner_count': len(batch_lines),
            'state': 'draft',
        })
        
        # Create SEPA batch lines
        for line_data in batch_lines:
            self.env['sepa.batch.line'].create({
                'batch_id': batch_history.id,
                'partner_id': line_data['partner_id'],
                'mandate_id': line_data['mandate_id'],
                'amount': line_data['amount'],
                'reference': line_data['reference'],
            })
        
        # Update next run date
        self._update_next_run_date()
        self.last_run_date = fields.Date.today()
        
        self.message_post(
            body=_("SEPA Batch generiert: %d Einträge, Gesamtbetrag: %.2f EUR") % (
                len(batch_lines), batch_history.total_amount
            )
        )
        
        return batch_history
    
    def _get_eligible_partners(self):
        """Get partners eligible for this batch"""
        domain = [('sepa_mandate_ids.state', '=', 'valid')]
        
        if self.partner_filter == 'specific':
            domain.append(('id', 'in', self.partner_ids.ids))
        elif self.partner_filter == 'tags':
            domain.append(('category_id', 'in', self.partner_tag_ids.ids))
        else:  # all
            # Add membership filter if products specified
            if self.membership_product_ids:
                domain.append(('member_lines.membership_id', 'in', self.membership_product_ids.ids))
        
        return self.env['res.partner'].search(domain)
    
    def _calculate_amount(self, partner):
        """Calculate amount for partner"""
        if self.amount_type == 'fixed':
            return self.fixed_amount
        elif self.amount_type == 'membership':
            # Get active membership
            today = fields.Date.today()
            member_line = partner.member_lines.filtered(
                lambda l: l.date_from <= today <= l.date_to and 
                l.state in ['paid', 'invoiced']
            )[:1]
            
            if member_line:
                # Calculate based on batch frequency
                if self.batch_type == 'monthly':
                    return member_line.price_total / 12
                elif self.batch_type == 'quarterly':
                    return member_line.price_total / 4
                elif self.batch_type == 'half_yearly':
                    return member_line.price_total / 2
                else:  # yearly
                    return member_line.price_total
            
            return 0
        else:  # custom
            # Would need custom field on partner
            return partner.custom_sepa_amount if hasattr(partner, 'custom_sepa_amount') else 0
    
    def _get_payment_reference(self, partner):
        """Generate payment reference for partner"""
        ref = f"Mitgliedsbeitrag {partner.name}"
        if self.batch_type == 'monthly':
            ref += f" {self.next_run_date.strftime('%m/%Y')}"
        elif self.batch_type == 'quarterly':
            quarter = (self.next_run_date.month - 1) // 3 + 1
            ref += f" Q{quarter}/{self.next_run_date.year}"
        elif self.batch_type == 'half_yearly':
            half = 1 if self.next_run_date.month <= 6 else 2
            ref += f" H{half}/{self.next_run_date.year}"
        else:  # yearly
            ref += f" {self.next_run_date.year}"
        
        return ref
    
    def _update_next_run_date(self):
        """Update next run date based on frequency"""
        if self.batch_type == 'monthly':
            next_date = self.next_run_date + relativedelta(months=1)
        elif self.batch_type == 'quarterly':
            next_date = self.next_run_date + relativedelta(months=3)
        elif self.batch_type == 'half_yearly':
            next_date = self.next_run_date + relativedelta(months=6)
        else:  # yearly
            next_date = self.next_run_date + relativedelta(years=1)
        
        # Ensure execution day is valid
        if self.execution_day:
            try:
                next_date = next_date.replace(day=min(self.execution_day, 28))
            except ValueError:
                pass
        
        self.next_run_date = next_date
    
    def action_generate_now(self):
        """Manual trigger to generate batch now"""
        self.ensure_one()
        batch = self.generate_batch()
        
        if batch:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'sepa.batch.history',
                'res_id': batch.id,
                'view_mode': 'form',
            }
        
        return False