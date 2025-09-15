# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'
    
    donation_certificate_id = fields.Many2one(
        'donation.certificate',
        string='Spendenbescheinigung',
        compute='_compute_donation_certificate',
        store=True
    )
    
    is_donation = fields.Boolean(
        string='Ist Spende',
        compute='_compute_is_donation',
        store=True
    )
    
    @api.depends('line_ids.account_id.nonprofit_type')
    def _compute_is_donation(self):
        for move in self:
            donation_accounts = move.line_ids.filtered(
                lambda l: l.account_id.nonprofit_type in ['donation', 'membership']
            )
            move.is_donation = bool(donation_accounts)
    
    @api.depends('is_donation')
    def _compute_donation_certificate(self):
        for move in self:
            if move.is_donation:
                certificate = self.env['donation.certificate'].search([
                    ('move_ids', 'in', move.id),
                    ('state', '!=', 'cancelled')
                ], limit=1)
                move.donation_certificate_id = certificate
            else:
                move.donation_certificate_id = False
    
    def action_create_donation_certificate(self):
        """Create donation certificate for this move"""
        self.ensure_one()
        
        if not self.is_donation:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': 'Fehler',
                    'message': 'Diese Buchung enthält keine Spenden oder Mitgliedsbeiträge.',
                    'type': 'danger',
                }
            }
        
        if self.donation_certificate_id:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'donation.certificate',
                'res_id': self.donation_certificate_id.id,
                'view_mode': 'form',
            }
        
        # Create new certificate
        certificate = self.env['donation.certificate'].create_from_moves([self.id])
        
        if certificate:
            return {
                'type': 'ir.actions.act_window',
                'res_model': 'donation.certificate',
                'res_id': certificate[0].id,
                'view_mode': 'form',
            }
        
        return False