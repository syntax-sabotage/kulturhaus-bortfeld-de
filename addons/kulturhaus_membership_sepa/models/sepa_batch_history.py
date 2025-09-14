# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime

class SepaBatchHistory(models.Model):
    _name = 'sepa.batch.history'
    _description = 'SEPA Batch History'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'batch_reference'
    
    batch_reference = fields.Char(
        string='Batch-Referenz',
        required=True,
        index=True,
        help='Eindeutige Referenz für diesen SEPA-Einzug'
    )
    
    batch_type = fields.Selection([
        ('full_year', 'Ganzjahresbeitrag'),
        ('half_year', 'Halbjahresbeitrag (Jan-Jun)'),
        ('half_year_2', 'Halbjahresbeitrag (Jul-Dez)'),
        ('custom', 'Benutzerdefiniert')
    ], string='Beitragsart', required=True)
    
    collection_date = fields.Date(
        string='Einzugsdatum',
        required=True,
        help='Datum der SEPA-Lastschrift'
    )
    
    member_count = fields.Integer(
        string='Anzahl Mitglieder',
        required=True,
        help='Anzahl der einbezogenen Mitglieder'
    )
    
    total_amount = fields.Float(
        string='Gesamtbetrag',
        required=True,
        help='Gesamtbetrag des Einzugs in EUR'
    )
    
    state = fields.Selection([
        ('draft', 'Entwurf'),
        ('generated', 'Generiert'),
        ('sent', 'An Bank gesendet'),
        ('processed', 'Verarbeitet'),
        ('cancelled', 'Storniert')
    ], string='Status', default='generated', tracking=True)
    
    xml_file = fields.Binary(
        string='SEPA XML-Datei',
        attachment=True,
        help='Die generierte SEPA XML-Datei'
    )
    
    xml_filename = fields.Char(
        string='Dateiname',
        help='Name der XML-Datei'
    )
    
    member_details = fields.Text(
        string='Mitglieder-Details',
        help='JSON mit Details zu den einbezogenen Mitgliedern'
    )
    
    notes = fields.Text(
        string='Notizen',
        help='Zusätzliche Notizen zu diesem Einzug'
    )
    
    # Tracking fields
    created_by = fields.Many2one(
        'res.users',
        string='Erstellt von',
        default=lambda self: self.env.user,
        readonly=True
    )
    
    sent_date = fields.Datetime(
        string='Gesendet am',
        help='Datum und Zeit, wann die Datei an die Bank gesendet wurde'
    )
    
    processed_date = fields.Datetime(
        string='Verarbeitet am',
        help='Datum und Zeit, wann die Bank den Einzug verarbeitet hat'
    )
    
    # Email notification tracking
    notification_sent = fields.Boolean(
        string='Benachrichtigung gesendet',
        default=False,
        help='Wurden die Mitglieder per E-Mail benachrichtigt?'
    )
    
    notification_date = fields.Datetime(
        string='Benachrichtigungsdatum',
        help='Wann wurden die E-Mail-Benachrichtigungen gesendet?'
    )
    
    failed_notifications = fields.Text(
        string='Fehlgeschlagene Benachrichtigungen',
        help='Liste der Mitglieder, bei denen die E-Mail-Benachrichtigung fehlschlug'
    )
    
    @api.model
    def create_from_wizard(self, wizard):
        """Create history record from SEPA batch wizard"""
        import json
        
        # Prepare member details
        member_details = []
        for member in wizard.member_ids:
            member_details.append({
                'id': member.id,
                'name': member.name,
                'iban': member.bank_account_iban[-4:] if member.bank_account_iban else '',  # Only last 4 digits
                'amount': wizard._get_amount_for_type(wizard.batch_type),
                'mandate_id': member.sepa_mandate_id
            })
        
        # Create history record
        history = self.create({
            'batch_reference': wizard.batch_reference,
            'batch_type': wizard.batch_type,
            'collection_date': wizard.collection_date,
            'member_count': len(wizard.member_ids),
            'total_amount': wizard.total_amount,
            'state': 'generated',
            'xml_file': wizard.sepa_xml_file,
            'xml_filename': wizard.sepa_xml_filename,
            'member_details': json.dumps(member_details, ensure_ascii=False),
        })
        
        return history
    
    def action_mark_sent(self):
        """Mark batch as sent to bank"""
        self.ensure_one()
        self.write({
            'state': 'sent',
            'sent_date': fields.Datetime.now()
        })
        return True
    
    def action_mark_processed(self):
        """Mark batch as processed by bank"""
        self.ensure_one()
        self.write({
            'state': 'processed',
            'processed_date': fields.Datetime.now()
        })
        return True
    
    def action_cancel(self):
        """Cancel this batch"""
        self.ensure_one()
        if self.state == 'processed':
            raise ValueError("Verarbeitete Einzüge können nicht storniert werden")
        self.state = 'cancelled'
        return True
    
    def action_send_notifications(self):
        """Send email notifications to members"""
        self.ensure_one()
        import json
        
        if not self.member_details:
            return False
        
        member_data = json.loads(self.member_details)
        failed = []
        success_count = 0
        
        # Get email template
        template = self.env.ref('kulturhaus_membership_sepa.email_template_sepa_notification', False)
        if not template:
            # Create a simple notification without template
            for member_info in member_data:
                member = self.env['res.partner'].browse(member_info['id'])
                if member.email:
                    try:
                        mail_values = {
                            'subject': f'SEPA-Lastschriftankündigung - Kulturhaus Bortfeld',
                            'body_html': self._get_notification_body(member, member_info['amount']),
                            'email_to': member.email,
                            'email_from': self.env.company.email or 'info@kulturhaus-bortfeld.de',
                        }
                        mail = self.env['mail.mail'].create(mail_values)
                        mail.send()
                        success_count += 1
                    except Exception as e:
                        failed.append(f"{member.name}: {str(e)}")
                else:
                    failed.append(f"{member.name}: Keine E-Mail-Adresse")
        
        # Update history record
        self.write({
            'notification_sent': True,
            'notification_date': fields.Datetime.now(),
            'failed_notifications': '\n'.join(failed) if failed else False
        })
        
        # Return notification
        if failed:
            message = f"✅ {success_count} Benachrichtigungen gesendet.\n❌ {len(failed)} fehlgeschlagen."
        else:
            message = f"✅ Alle {success_count} Benachrichtigungen erfolgreich gesendet!"
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': 'E-Mail-Benachrichtigungen',
                'message': message,
                'type': 'success' if not failed else 'warning',
                'sticky': False,
            }
        }
    
    def _get_notification_body(self, member, amount):
        """Generate email body for SEPA notification"""
        return f"""
        <p>Sehr geehrte/r {member.name},</p>
        
        <p>hiermit informieren wir Sie über die anstehende SEPA-Lastschrift für Ihren Mitgliedsbeitrag:</p>
        
        <table style="margin: 20px 0;">
            <tr><td style="padding: 5px;"><strong>Betrag:</strong></td><td>{amount:.2f} EUR</td></tr>
            <tr><td style="padding: 5px;"><strong>Einzugsdatum:</strong></td><td>{self.collection_date.strftime('%d.%m.%Y')}</td></tr>
            <tr><td style="padding: 5px;"><strong>Mandatsreferenz:</strong></td><td>{member.sepa_mandate_id or 'N/A'}</td></tr>
            <tr><td style="padding: 5px;"><strong>Verwendungszweck:</strong></td><td>Mitgliedsbeitrag {self.collection_date.year}</td></tr>
        </table>
        
        <p>Bitte sorgen Sie für ausreichende Deckung auf Ihrem Konto.</p>
        
        <p>Bei Fragen wenden Sie sich bitte an unsere Geschäftsstelle.</p>
        
        <p>Mit freundlichen Grüßen<br/>
        Kulturhaus Bortfeld e.V.</p>
        
        <hr style="margin-top: 30px;"/>
        <p style="font-size: 0.9em; color: #666;">
        Kulturhaus Bortfeld e.V.<br/>
        Mitgliederbetreuung<br/>
        E-Mail: mitglieder@kulturhaus-bortfeld.de<br/>
        Web: www.kulturhaus-bortfeld.de
        </p>
        """
    
    def action_download_xml(self):
        """Download the XML file"""
        self.ensure_one()
        if not self.xml_file:
            raise ValueError("Keine XML-Datei vorhanden")
        
        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/?model={self._name}&id={self.id}&field=xml_file&filename_field=xml_filename&download=true',
            'target': 'self',
        }
    
    @api.model
    def get_statistics(self):
        """Get statistics for dashboard"""
        total_batches = self.search_count([])
        total_amount = sum(self.search([]).mapped('total_amount'))
        last_batch = self.search([], limit=1, order='create_date desc')
        
        return {
            'total_batches': total_batches,
            'total_amount': total_amount,
            'last_batch_date': last_batch.collection_date if last_batch else False,
            'last_batch_amount': last_batch.total_amount if last_batch else 0,
        }