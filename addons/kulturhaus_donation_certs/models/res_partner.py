# -*- coding: utf-8 -*-
from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    donation_certificate_ids = fields.One2many(
        'donation.certificate',
        'partner_id',
        string='Spendenbescheinigungen'
    )
    
    donation_certificate_count = fields.Integer(
        string='Anzahl Spendenbescheinigungen',
        compute='_compute_donation_certificate_count'
    )
    
    total_donations = fields.Monetary(
        string='Gesamtspenden',
        compute='_compute_total_donations',
        currency_field='currency_id'
    )
    
    wants_donation_certificate = fields.Boolean(
        string='Möchte Spendenbescheinigung',
        default=True,
        help='Gibt an, ob der Kontakt Spendenbescheinigungen erhalten möchte'
    )
    
    donation_certificate_email = fields.Boolean(
        string='Spendenbescheinigung per E-Mail',
        default=True,
        help='Spendenbescheinigung per E-Mail statt per Post versenden'
    )
    
    @api.depends('donation_certificate_ids')
    def _compute_donation_certificate_count(self):
        for partner in self:
            partner.donation_certificate_count = len(partner.donation_certificate_ids)
    
    @api.depends('donation_certificate_ids.amount_total', 'donation_certificate_ids.state')
    def _compute_total_donations(self):
        for partner in self:
            certificates = partner.donation_certificate_ids.filtered(
                lambda c: c.state in ['confirmed', 'sent']
            )
            partner.total_donations = sum(certificates.mapped('amount_total'))
    
    def action_view_donation_certificates(self):
        """Open donation certificates for this partner"""
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Spendenbescheinigungen',
            'res_model': 'donation.certificate',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }