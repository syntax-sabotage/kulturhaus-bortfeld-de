# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date

class AnnualCertificateWizard(models.TransientModel):
    _name = 'annual.certificate.wizard'
    _description = 'Jahres-Spendenbescheinigungen Assistent'
    
    year = fields.Integer(
        string='Jahr',
        required=True,
        default=lambda self: date.today().year - 1
    )
    
    partner_ids = fields.Many2many(
        'res.partner',
        string='Spender',
        help='Leer lassen für alle Spender'
    )
    
    min_amount = fields.Monetary(
        string='Mindestbetrag',
        currency_field='currency_id',
        default=0,
        help='Nur Spender mit mindestens diesem Gesamtbetrag'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    certificate_type = fields.Selection([
        ('collective', 'Sammelbestätigungen'),
        ('single', 'Einzelbestätigungen'),
    ], string='Art', default='collective', required=True)
    
    send_email = fields.Boolean(
        string='Per E-Mail versenden',
        default=True
    )
    
    only_with_email = fields.Boolean(
        string='Nur mit E-Mail-Adresse',
        default=False
    )
    
    preview_count = fields.Integer(
        string='Anzahl Bescheinigungen',
        compute='_compute_preview'
    )
    
    preview_amount = fields.Monetary(
        string='Gesamtbetrag',
        compute='_compute_preview',
        currency_field='currency_id'
    )
    
    @api.depends('year', 'partner_ids', 'min_amount', 'only_with_email')
    def _compute_preview(self):
        for wizard in self:
            date_from = date(wizard.year, 1, 1)
            date_to = date(wizard.year, 12, 31)
            
            # Find all relevant moves
            domain = [
                ('date', '>=', date_from),
                ('date', '<=', date_to),
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'entry']),
            ]
            
            if wizard.partner_ids:
                domain.append(('partner_id', 'in', wizard.partner_ids.ids))
            
            moves = self.env['account.move'].search(domain)
            
            # Group by partner and calculate amounts
            partner_amounts = {}
            for move in moves:
                if not move.partner_id:
                    continue
                
                # Skip if email required but not present
                if wizard.only_with_email and not move.partner_id.email:
                    continue
                
                # Skip if partner doesn't want certificates
                if not move.partner_id.wants_donation_certificate:
                    continue
                
                # Check for donation/membership accounts
                amount = 0
                for line in move.line_ids:
                    if line.account_id.nonprofit_type in ['donation', 'membership']:
                        amount += abs(line.credit - line.debit)
                
                if amount > 0:
                    if move.partner_id not in partner_amounts:
                        partner_amounts[move.partner_id] = 0
                    partner_amounts[move.partner_id] += amount
            
            # Apply minimum amount filter
            if wizard.min_amount > 0:
                partner_amounts = {
                    p: a for p, a in partner_amounts.items() 
                    if a >= wizard.min_amount
                }
            
            wizard.preview_count = len(partner_amounts)
            wizard.preview_amount = sum(partner_amounts.values())
    
    def action_create_certificates(self):
        """Create annual donation certificates"""
        self.ensure_one()
        
        date_from = date(self.year, 1, 1)
        date_to = date(self.year, 12, 31)
        
        # Find all relevant moves
        domain = [
            ('date', '>=', date_from),
            ('date', '<=', date_to),
            ('state', '=', 'posted'),
            ('move_type', 'in', ['out_invoice', 'entry']),
        ]
        
        if self.partner_ids:
            domain.append(('partner_id', 'in', self.partner_ids.ids))
        
        moves = self.env['account.move'].search(domain)
        
        # Group by partner
        partner_moves = {}
        for move in moves:
            if not move.partner_id:
                continue
            
            # Skip if email required but not present
            if self.only_with_email and not move.partner_id.email:
                continue
            
            # Skip if partner doesn't want certificates
            if not move.partner_id.wants_donation_certificate:
                continue
            
            # Check if already has certificate
            existing = self.env['donation.certificate'].search([
                ('move_ids', 'in', move.id),
                ('state', '!=', 'cancelled')
            ])
            if existing:
                continue
            
            # Check for donation/membership accounts
            has_relevant = False
            for line in move.line_ids:
                if line.account_id.nonprofit_type in ['donation', 'membership']:
                    has_relevant = True
                    break
            
            if has_relevant:
                if move.partner_id not in partner_moves:
                    partner_moves[move.partner_id] = []
                partner_moves[move.partner_id].append(move)
        
        # Create certificates
        certificates = self.env['donation.certificate']
        for partner, partner_move_list in partner_moves.items():
            # Calculate total amount
            total_amount = 0
            for move in partner_move_list:
                for line in move.line_ids:
                    if line.account_id.nonprofit_type in ['donation', 'membership']:
                        total_amount += abs(line.credit - line.debit)
            
            # Apply minimum amount filter
            if self.min_amount > 0 and total_amount < self.min_amount:
                continue
            
            # Create certificate
            cert = self.env['donation.certificate'].create_from_moves(
                [m.id for m in partner_move_list]
            )
            if cert:
                certificates |= cert
                
                # Auto-confirm and send if requested
                cert.action_confirm()
                if self.send_email and partner.email and partner.donation_certificate_email:
                    cert.action_send()
        
        if certificates:
            return {
                'type': 'ir.actions.act_window',
                'name': _('Erstellte Spendenbescheinigungen'),
                'res_model': 'donation.certificate',
                'view_mode': 'list,form',
                'domain': [('id', 'in', certificates.ids)],
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Keine Bescheinigungen'),
                    'message': _('Keine neuen Spendenbescheinigungen erstellt.'),
                    'type': 'info',
                }
            }