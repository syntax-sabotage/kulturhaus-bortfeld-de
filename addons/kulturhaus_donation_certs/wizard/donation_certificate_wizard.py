# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, date

class DonationCertificateWizard(models.TransientModel):
    _name = 'donation.certificate.wizard'
    _description = 'Spendenbescheinigung Assistent'
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Spender',
        required=True
    )
    
    date_from = fields.Date(
        string='Von Datum',
        required=True,
        default=lambda self: date(date.today().year, 1, 1)
    )
    
    date_to = fields.Date(
        string='Bis Datum',
        required=True,
        default=fields.Date.context_today
    )
    
    certificate_type = fields.Selection([
        ('single', 'Einzelbestätigung'),
        ('collective', 'Sammelbestätigung'),
    ], string='Art', default='collective', required=True)
    
    include_donations = fields.Boolean(
        string='Spenden einschließen',
        default=True
    )
    
    include_membership = fields.Boolean(
        string='Mitgliedsbeiträge einschließen',
        default=True
    )
    
    only_uncertified = fields.Boolean(
        string='Nur unbescheinite Buchungen',
        default=True,
        help='Nur Buchungen ohne existierende Spendenbescheinigung berücksichtigen'
    )
    
    move_ids = fields.Many2many(
        'account.move',
        string='Gefundene Buchungen',
        compute='_compute_move_ids'
    )
    
    amount_preview = fields.Monetary(
        string='Vorschau Betrag',
        compute='_compute_amount_preview',
        currency_field='currency_id'
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        default=lambda self: self.env.company.currency_id
    )
    
    @api.depends('partner_id', 'date_from', 'date_to', 'include_donations', 
                 'include_membership', 'only_uncertified')
    def _compute_move_ids(self):
        for wizard in self:
            if not wizard.partner_id or not wizard.date_from or not wizard.date_to:
                wizard.move_ids = False
                continue
            
            domain = [
                ('partner_id', '=', wizard.partner_id.id),
                ('date', '>=', wizard.date_from),
                ('date', '<=', wizard.date_to),
                ('state', '=', 'posted'),
                ('move_type', 'in', ['out_invoice', 'entry']),
            ]
            
            moves = self.env['account.move'].search(domain)
            
            # Filter by donation/membership accounts
            filtered_moves = self.env['account.move']
            for move in moves:
                has_donation = False
                has_membership = False
                
                for line in move.line_ids:
                    if line.account_id.nonprofit_type == 'donation' and wizard.include_donations:
                        has_donation = True
                    elif line.account_id.nonprofit_type == 'membership' and wizard.include_membership:
                        has_membership = True
                
                if has_donation or has_membership:
                    # Check if already certified
                    if wizard.only_uncertified:
                        existing = self.env['donation.certificate'].search([
                            ('move_ids', 'in', move.id),
                            ('state', '!=', 'cancelled')
                        ])
                        if not existing:
                            filtered_moves |= move
                    else:
                        filtered_moves |= move
            
            wizard.move_ids = filtered_moves
    
    @api.depends('move_ids')
    def _compute_amount_preview(self):
        for wizard in self:
            total = 0
            for move in wizard.move_ids:
                for line in move.line_ids:
                    if line.account_id.nonprofit_type in ['donation', 'membership']:
                        total += abs(line.credit - line.debit)
            wizard.amount_preview = total
    
    def action_create_certificate(self):
        """Create donation certificate"""
        self.ensure_one()
        
        if not self.move_ids:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Keine Buchungen'),
                    'message': _('Keine passenden Buchungen gefunden.'),
                    'type': 'warning',
                }
            }
        
        # Create certificate
        certificates = self.env['donation.certificate'].create_from_moves(self.move_ids.ids)
        
        if len(certificates) == 1:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'donation.certificate',
                'res_id': certificates[0].id,
                'view_mode': 'form',
            }
        else:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'donation.certificate',
                'domain': [('id', 'in', certificates.ids)],
                'view_mode': 'list,form',
            }