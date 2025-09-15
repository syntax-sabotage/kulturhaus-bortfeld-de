# -*- coding: utf-8 -*-
import qrcode
import io
import base64
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class DonationCertificate(models.Model):
    _name = 'donation.certificate'
    _description = 'Zuwendungsbescheinigung'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'date desc, name desc'
    
    name = fields.Char(
        string='Nummer',
        required=True,
        readonly=True,
        default='Neu',
        copy=False
    )
    
    partner_id = fields.Many2one(
        'res.partner',
        string='Spender',
        required=True,
        tracking=True
    )
    
    date = fields.Date(
        string='Ausstellungsdatum',
        required=True,
        default=fields.Date.context_today,
        tracking=True
    )
    
    year = fields.Integer(
        string='Jahr',
        required=True,
        compute='_compute_year',
        store=True
    )
    
    certificate_type = fields.Selection([
        ('single', 'Einzelbestätigung'),
        ('collective', 'Sammelbestätigung'),
    ], string='Art', default='single', required=True)
    
    donation_type = fields.Selection([
        ('money', 'Geldspende'),
        ('goods', 'Sachspende'),
        ('membership', 'Mitgliedsbeitrag'),
        ('mixed', 'Gemischt'),
    ], string='Spendenart', default='money', required=True)
    
    amount_money = fields.Monetary(
        string='Geldzuwendung',
        currency_field='currency_id',
        tracking=True
    )
    
    amount_goods = fields.Monetary(
        string='Sachzuwendung',
        currency_field='currency_id',
        tracking=True
    )
    
    amount_membership = fields.Monetary(
        string='Mitgliedsbeitrag',
        currency_field='currency_id',
        tracking=True
    )
    
    amount_total = fields.Monetary(
        string='Gesamtbetrag',
        currency_field='currency_id',
        compute='_compute_amount_total',
        store=True
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Währung',
        default=lambda self: self.env.company.currency_id,
        required=True
    )
    
    goods_description = fields.Text(
        string='Beschreibung Sachspende'
    )
    
    period_from = fields.Date(
        string='Zeitraum von'
    )
    
    period_to = fields.Date(
        string='Zeitraum bis'
    )
    
    move_ids = fields.Many2many(
        'account.move',
        string='Verknüpfte Buchungen'
    )
    
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('confirmed', 'Bestätigt'),
        ('sent', 'Versendet'),
        ('cancelled', 'Storniert'),
    ], string='Status', default='draft', tracking=True)
    
    company_id = fields.Many2one(
        'res.company',
        string='Verein',
        required=True,
        default=lambda self: self.env.company
    )
    
    # Legal text fields
    legal_notice = fields.Text(
        string='Rechtlicher Hinweis',
        compute='_compute_legal_notice'
    )
    
    qr_code = fields.Binary(
        string='QR Code',
        compute='_compute_qr_code'
    )
    
    # Email fields
    email_sent = fields.Boolean(
        string='E-Mail versendet',
        default=False
    )
    
    email_date = fields.Datetime(
        string='E-Mail Datum'
    )
    
    @api.depends('date')
    def _compute_year(self):
        for record in self:
            record.year = record.date.year if record.date else datetime.now().year
    
    @api.depends('amount_money', 'amount_goods', 'amount_membership')
    def _compute_amount_total(self):
        for record in self:
            record.amount_total = (
                record.amount_money + 
                record.amount_goods + 
                record.amount_membership
            )
    
    @api.depends('donation_type', 'amount_total')
    def _compute_legal_notice(self):
        for record in self:
            if record.donation_type == 'money':
                record.legal_notice = self._get_money_donation_text()
            elif record.donation_type == 'goods':
                record.legal_notice = self._get_goods_donation_text()
            elif record.donation_type == 'membership':
                record.legal_notice = self._get_membership_text()
            else:
                record.legal_notice = self._get_mixed_donation_text()
    
    def _get_money_donation_text(self):
        """Get legal text for money donations"""
        return """
Bestätigung über Geldzuwendung im Sinne des § 10b des Einkommensteuergesetzes 
an eine der in § 5 Abs. 1 Nr. 9 des Körperschaftsteuergesetzes bezeichneten 
Körperschaften, Personenvereinigungen oder Vermögensmassen.

Wir sind wegen Förderung der Kultur nach dem letzten uns zugegangenen 
Freistellungsbescheid des Finanzamtes {tax_office} vom {certificate_date}
nach § 5 Abs. 1 Nr. 9 des Körperschaftsteuergesetzes von der Körperschaftsteuer 
und nach § 3 Nr. 6 des Gewerbesteuergesetzes von der Gewerbesteuer befreit.

Es wird bestätigt, dass die Zuwendung nur zur Förderung der Kultur verwendet wird.
""".format(
            tax_office=self.company_id.tax_office or '[Finanzamt]',
            certificate_date=self.company_id.nonprofit_certificate_date or '[Datum]'
        )
    
    def _get_goods_donation_text(self):
        """Get legal text for goods donations"""
        return """
Bestätigung über Sachzuwendung im Sinne des § 10b des Einkommensteuergesetzes 
an eine der in § 5 Abs. 1 Nr. 9 des Körperschaftsteuergesetzes bezeichneten 
Körperschaften, Personenvereinigungen oder Vermögensmassen.

Die Sachzuwendung wurde zur Förderung der Kultur verwendet.

Grundlage der Bewertung: Marktüblicher Preis/Wiederbeschaffungswert.
"""
    
    def _get_membership_text(self):
        """Get legal text for membership fees"""
        return """
Bestätigung über Mitgliedsbeitrag

Mitgliedsbeiträge an Kulturvereine sind nach § 10b EStG als Sonderausgaben 
abzugsfähig, wenn der Verein ausschließlich und unmittelbar gemeinnützige 
Zwecke verfolgt.

Der Mitgliedsbeitrag wurde ausschließlich für satzungsgemäße Zwecke verwendet.
"""
    
    def _get_mixed_donation_text(self):
        """Get legal text for mixed donations"""
        return self._get_money_donation_text()
    
    @api.depends('name', 'partner_id', 'amount_total')
    def _compute_qr_code(self):
        for record in self:
            if record.name and record.name != 'Neu':
                qr_data = self._generate_qr_data()
                qr = qrcode.QRCode(version=1, box_size=10, border=4)
                qr.add_data(qr_data)
                qr.make(fit=True)
                
                img = qr.make_image(fill_color="black", back_color="white")
                buffer = io.BytesIO()
                img.save(buffer, format='PNG')
                record.qr_code = base64.b64encode(buffer.getvalue())
            else:
                record.qr_code = False
    
    def _generate_qr_data(self):
        """Generate QR code data for tax authority"""
        return (
            f"BCD\n001\n1\nSCT\n"
            f"{self.company_id.name}\n"
            f"{self.company_id.vat or ''}\n"
            f"EUR{self.amount_total:.2f}\n"
            f"CHAR\n"
            f"Spendenbescheinigung {self.name}\n"
            f"{self.partner_id.name}\n"
        )
    
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'Neu') == 'Neu':
                vals['name'] = self.env['ir.sequence'].next_by_code('donation.certificate') or 'Neu'
        return super().create(vals_list)
    
    @api.constrains('amount_total')
    def _check_amount(self):
        for record in self:
            if record.amount_total <= 0:
                raise ValidationError(_('Der Betrag muss größer als 0 sein.'))
    
    @api.constrains('period_from', 'period_to')
    def _check_period(self):
        for record in self:
            if record.certificate_type == 'collective':
                if not record.period_from or not record.period_to:
                    raise ValidationError(_('Bei Sammelbestätigungen muss ein Zeitraum angegeben werden.'))
                if record.period_from > record.period_to:
                    raise ValidationError(_('Das Enddatum muss nach dem Startdatum liegen.'))
    
    def action_confirm(self):
        """Confirm the donation certificate"""
        self.ensure_one()
        if self.state != 'draft':
            raise UserError(_('Nur Entwürfe können bestätigt werden.'))
        
        self.state = 'confirmed'
        
        # Create activity for sending
        self.activity_schedule(
            'mail.mail_activity_data_todo',
            summary=_('Spendenbescheinigung versenden'),
            user_id=self.env.user.id
        )
    
    def action_send(self):
        """Send the donation certificate by email"""
        self.ensure_one()
        if self.state not in ['confirmed', 'sent']:
            raise UserError(_('Nur bestätigte Bescheinigungen können versendet werden.'))
        
        # Generate and send email with PDF attachment
        template = self.env.ref('kulturhaus_donation_certs.email_template_donation_certificate', False)
        if template:
            template.send_mail(self.id, force_send=True)
        
        self.write({
            'state': 'sent',
            'email_sent': True,
            'email_date': fields.Datetime.now(),
        })
    
    def action_cancel(self):
        """Cancel the donation certificate"""
        self.ensure_one()
        if self.state == 'cancelled':
            raise UserError(_('Bereits stornierte Bescheinigung.'))
        
        self.state = 'cancelled'
    
    def action_draft(self):
        """Reset to draft"""
        self.ensure_one()
        self.state = 'draft'
    
    def action_print(self):
        """Print the donation certificate"""
        self.ensure_one()
        return self.env.ref('kulturhaus_donation_certs.action_report_donation_certificate').report_action(self)
    
    @api.model
    def create_from_moves(self, move_ids):
        """Create donation certificate from account moves"""
        moves = self.env['account.move'].browse(move_ids)
        
        # Group by partner
        partner_moves = {}
        for move in moves:
            if move.partner_id:
                if move.partner_id not in partner_moves:
                    partner_moves[move.partner_id] = []
                partner_moves[move.partner_id].append(move)
        
        certificates = self.env['donation.certificate']
        for partner, partner_move_list in partner_moves.items():
            # Calculate amounts by type
            amount_money = 0
            amount_membership = 0
            
            for move in partner_move_list:
                for line in move.line_ids:
                    if line.account_id.nonprofit_type == 'donation':
                        amount_money += abs(line.credit - line.debit)
                    elif line.account_id.nonprofit_type == 'membership':
                        amount_membership += abs(line.credit - line.debit)
            
            if amount_money > 0 or amount_membership > 0:
                donation_type = 'mixed'
                if amount_money > 0 and amount_membership == 0:
                    donation_type = 'money'
                elif amount_membership > 0 and amount_money == 0:
                    donation_type = 'membership'
                
                vals = {
                    'partner_id': partner.id,
                    'certificate_type': 'collective' if len(partner_move_list) > 1 else 'single',
                    'donation_type': donation_type,
                    'amount_money': amount_money,
                    'amount_membership': amount_membership,
                    'move_ids': [(6, 0, [m.id for m in partner_move_list])],
                    'period_from': min(m.date for m in partner_move_list),
                    'period_to': max(m.date for m in partner_move_list),
                }
                
                certificate = self.create(vals)
                certificates |= certificate
        
        return certificates