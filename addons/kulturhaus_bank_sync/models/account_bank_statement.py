# -*- coding: utf-8 -*-
import base64
import csv
import io
from datetime import datetime
from lxml import etree
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountBankStatement(models.Model):
    _inherit = 'account.bank.statement'
    
    import_source = fields.Selection([
        ('manual', 'Manuell'),
        ('csv', 'CSV Import'),
        ('camt', 'CAMT.053 Import'),
        ('stripe', 'Stripe API'),
        ('sepa', 'SEPA'),
    ], string='Import Quelle', default='manual')
    
    unreconciled_count = fields.Integer(
        string='Unabgestimmte Posten',
        compute='_compute_unreconciled_count'
    )
    
    auto_reconciled_count = fields.Integer(
        string='Automatisch abgestimmt',
        default=0
    )
    
    @api.depends('line_ids.is_reconciled')
    def _compute_unreconciled_count(self):
        for statement in self:
            statement.unreconciled_count = len(
                statement.line_ids.filtered(lambda l: not l.is_reconciled)
            )
    
    def import_csv_file(self, file_content, encoding='utf-8'):
        """Import bank statement from CSV file"""
        try:
            csv_data = base64.b64decode(file_content)
            csv_file = io.StringIO(csv_data.decode(encoding))
            reader = csv.DictReader(csv_file, delimiter=';')
            
            lines = []
            for row in reader:
                # Parse German date format and amounts
                date_str = row.get('Buchungstag', row.get('Date', ''))
                amount_str = row.get('Betrag', row.get('Amount', '0'))
                
                # Convert German number format
                amount = float(amount_str.replace('.', '').replace(',', '.'))
                
                # Parse date
                if '.' in date_str:  # German format DD.MM.YYYY
                    date = datetime.strptime(date_str, '%d.%m.%Y').date()
                else:
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                lines.append({
                    'date': date,
                    'payment_ref': row.get('Verwendungszweck', row.get('Reference', '')),
                    'partner_name': row.get('Empfänger/Zahlungspflichtiger', row.get('Partner', '')),
                    'amount': amount,
                    'narration': row.get('Buchungstext', ''),
                })
            
            return self._create_statement_lines(lines)
            
        except Exception as e:
            raise UserError(_('Fehler beim CSV Import: %s') % str(e))
    
    def import_camt053_file(self, file_content):
        """Import bank statement from CAMT.053 XML file"""
        try:
            xml_data = base64.b64decode(file_content)
            root = etree.fromstring(xml_data)
            
            # Remove namespace for easier parsing
            for elem in root.getiterator():
                if '}' in elem.tag:
                    elem.tag = elem.tag.split('}')[1]
            
            lines = []
            for entry in root.findall('.//Ntry'):
                amount_elem = entry.find('.//Amt')
                amount = float(amount_elem.text)
                if entry.find('.//CdtDbtInd').text == 'DBIT':
                    amount = -amount
                
                date_str = entry.find('.//BookgDt/Dt').text
                date = datetime.strptime(date_str, '%Y-%m-%d').date()
                
                # Extract partner info
                partner_name = ''
                partner_elem = entry.find('.//RltdPties/Cdtr/Nm')
                if partner_elem is None:
                    partner_elem = entry.find('.//RltdPties/Dbtr/Nm')
                if partner_elem is not None:
                    partner_name = partner_elem.text
                
                # Extract reference
                ref_elem = entry.find('.//RmtInf/Ustrd')
                reference = ref_elem.text if ref_elem is not None else ''
                
                lines.append({
                    'date': date,
                    'payment_ref': reference,
                    'partner_name': partner_name,
                    'amount': amount,
                    'narration': entry.find('.//AddtlNtryInf').text if entry.find('.//AddtlNtryInf') is not None else '',
                })
            
            return self._create_statement_lines(lines)
            
        except Exception as e:
            raise UserError(_('Fehler beim CAMT.053 Import: %s') % str(e))
    
    def _create_statement_lines(self, lines_data):
        """Create bank statement lines from imported data"""
        statement_lines = []
        for line_data in lines_data:
            vals = {
                'date': line_data['date'],
                'payment_ref': line_data.get('payment_ref', ''),
                'partner_name': line_data.get('partner_name', ''),
                'amount': line_data['amount'],
                'narration': line_data.get('narration', ''),
            }
            
            # Try to find partner
            if line_data.get('partner_name'):
                partner = self.env['res.partner'].search([
                    ('name', 'ilike', line_data['partner_name'])
                ], limit=1)
                if partner:
                    vals['partner_id'] = partner.id
            
            statement_lines.append((0, 0, vals))
        
        self.line_ids = statement_lines
        return True
    
    def action_auto_reconcile(self):
        """Automatically reconcile statement lines using rules"""
        self.ensure_one()
        reconciled_count = 0
        
        rules = self.env['bank.reconciliation.rule'].search([], order='sequence')
        
        for line in self.line_ids.filtered(lambda l: not l.is_reconciled):
            for rule in rules:
                if rule.apply_rule(line):
                    reconciled_count += 1
                    break
        
        self.auto_reconciled_count = reconciled_count
        
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Automatische Abstimmung'),
                'message': _('%d Posten wurden automatisch abgestimmt.') % reconciled_count,
                'type': 'success',
            }
        }


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'
    
    reconciliation_status = fields.Selection([
        ('unreconciled', 'Unabgestimmt'),
        ('partial', 'Teilweise abgestimmt'),
        ('reconciled', 'Abgestimmt'),
    ], string='Abstimmungsstatus', compute='_compute_reconciliation_status', store=True)
    
    stripe_payment_id = fields.Char(
        string='Stripe Payment ID',
        help='Verknüpfte Stripe Zahlung'
    )
    
    sepa_mandate_id = fields.Char(
        string='SEPA Mandat ID',
        help='Verknüpftes SEPA Mandat'
    )
    
    suggested_partner_id = fields.Many2one(
        'res.partner',
        string='Vorgeschlagener Partner',
        compute='_compute_suggested_partner'
    )
    
    @api.depends('is_reconciled', 'amount_residual')
    def _compute_reconciliation_status(self):
        for line in self:
            if line.is_reconciled:
                line.reconciliation_status = 'reconciled'
            elif line.amount_residual != line.amount:
                line.reconciliation_status = 'partial'
            else:
                line.reconciliation_status = 'unreconciled'
    
    @api.depends('payment_ref', 'partner_name')
    def _compute_suggested_partner(self):
        for line in self:
            if line.partner_id:
                line.suggested_partner_id = False
                continue
            
            # Try to find partner by name or reference
            partner = False
            if line.partner_name:
                partner = self.env['res.partner'].search([
                    ('name', 'ilike', line.partner_name)
                ], limit=1)
            
            if not partner and line.payment_ref:
                # Try to find by reference patterns
                if 'STRIPE' in line.payment_ref.upper():
                    # Look for Stripe customer
                    pass
                elif 'SEPA' in line.payment_ref.upper():
                    # Look for SEPA mandate
                    pass
            
            line.suggested_partner_id = partner