# -*- coding: utf-8 -*-
import base64
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BankImportWizard(models.TransientModel):
    _name = 'bank.import.wizard'
    _description = 'Bank Import Assistent'
    
    import_type = fields.Selection([
        ('csv', 'CSV Datei'),
        ('camt', 'CAMT.053 XML'),
    ], string='Import Typ', required=True, default='csv')
    
    file_data = fields.Binary(
        string='Datei',
        required=True
    )
    
    file_name = fields.Char(
        string='Dateiname'
    )
    
    journal_id = fields.Many2one(
        'account.journal',
        string='Bank Journal',
        required=True,
        domain=[('type', '=', 'bank')]
    )
    
    encoding = fields.Selection([
        ('utf-8', 'UTF-8'),
        ('iso-8859-1', 'ISO-8859-1'),
        ('windows-1252', 'Windows-1252'),
    ], string='Dateikodierung', default='utf-8')
    
    auto_reconcile = fields.Boolean(
        string='Automatische Abstimmung',
        default=True,
        help='Versucht nach dem Import automatisch abzustimmen'
    )
    
    statement_date = fields.Date(
        string='Auszugsdatum',
        default=fields.Date.context_today,
        required=True
    )
    
    def action_import(self):
        """Import bank statement file"""
        self.ensure_one()
        
        if not self.file_data:
            raise UserError(_('Bitte wählen Sie eine Datei aus.'))
        
        # Create bank statement
        statement = self.env['account.bank.statement'].create({
            'name': f'Import {self.statement_date}',
            'journal_id': self.journal_id.id,
            'date': self.statement_date,
            'import_source': 'csv' if self.import_type == 'csv' else 'camt',
        })
        
        # Import based on type
        try:
            if self.import_type == 'csv':
                statement.import_csv_file(self.file_data, self.encoding)
            else:  # camt
                statement.import_camt053_file(self.file_data)
        except Exception as e:
            statement.unlink()
            raise UserError(_('Import fehlgeschlagen: %s') % str(e))
        
        # Auto reconcile if requested
        if self.auto_reconcile:
            statement.action_auto_reconcile()
        
        # Return action to show the statement
        return {
            'type': 'ir.actions.act_window',
            'name': _('Bank Auszug'),
            'res_model': 'account.bank.statement',
            'res_id': statement.id,
            'view_mode': 'form',
            'target': 'current',
        }