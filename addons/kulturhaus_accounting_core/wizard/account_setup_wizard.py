# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import date

class AccountSetupWizard(models.TransientModel):
    _name = 'account.setup.wizard'
    _description = 'Buchhaltung Einrichtungsassistent'
    
    company_id = fields.Many2one(
        'res.company',
        string='Verein',
        required=True,
        default=lambda self: self.env.company
    )
    
    create_fiscal_year = fields.Boolean(
        string='Geschäftsjahr anlegen',
        default=True
    )
    
    fiscal_year_start = fields.Date(
        string='Geschäftsjahr Beginn',
        default=lambda self: date(date.today().year, 1, 1)
    )
    
    fiscal_year_end = fields.Date(
        string='Geschäftsjahr Ende',
        default=lambda self: date(date.today().year, 12, 31)
    )
    
    load_skr49 = fields.Boolean(
        string='SKR49 Kontenrahmen laden',
        default=True,
        help='Lädt den SKR49 Kontenrahmen für gemeinnützige Vereine'
    )
    
    setup_taxes = fields.Boolean(
        string='Steuern einrichten',
        default=True,
        help='Richtet deutsche Steuersätze ein (0%, 7%, 19%)'
    )
    
    migrate_existing = fields.Boolean(
        string='Bestehende Buchungen migrieren',
        default=False,
        help='Versucht bestehende Buchungen auf neue Konten zu übertragen'
    )
    
    def action_setup(self):
        """Execute the setup wizard"""
        self.ensure_one()
        
        # Step 1: Load SKR49 chart of accounts
        if self.load_skr49:
            self.env['account.account'].create_skr49_accounts()
            
        # Step 2: Setup taxes
        if self.setup_taxes:
            self._setup_german_taxes()
            
        # Step 3: Create fiscal year
        if self.create_fiscal_year:
            self._create_fiscal_year()
            
        # Step 4: Migrate existing entries if requested
        if self.migrate_existing:
            self._migrate_existing_entries()
            
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Einrichtung abgeschlossen'),
                'message': _('Die Buchhaltung wurde erfolgreich eingerichtet.'),
                'type': 'success',
                'sticky': False,
            }
        }
    
    def _setup_german_taxes(self):
        """Setup German tax rates"""
        tax_data = [
            {
                'name': 'MwSt. 19% (Verkauf)',
                'amount': 19.0,
                'type_tax_use': 'sale',
                'tax_group_id': self.env.ref('account.tax_group_taxes').id,
            },
            {
                'name': 'MwSt. 7% (Verkauf)',
                'amount': 7.0,
                'type_tax_use': 'sale',
                'tax_group_id': self.env.ref('account.tax_group_taxes').id,
            },
            {
                'name': 'Steuerbefreit (Verkauf)',
                'amount': 0.0,
                'type_tax_use': 'sale',
                'tax_group_id': self.env.ref('account.tax_group_taxes').id,
            },
            {
                'name': 'Vorsteuer 19% (Einkauf)',
                'amount': 19.0,
                'type_tax_use': 'purchase',
                'tax_group_id': self.env.ref('account.tax_group_taxes').id,
            },
            {
                'name': 'Vorsteuer 7% (Einkauf)',
                'amount': 7.0,
                'type_tax_use': 'purchase',
                'tax_group_id': self.env.ref('account.tax_group_taxes').id,
            },
        ]
        
        for tax_vals in tax_data:
            existing = self.env['account.tax'].search([
                ('name', '=', tax_vals['name']),
                ('company_id', '=', self.company_id.id)
            ])
            if not existing:
                tax_vals['company_id'] = self.company_id.id
                self.env['account.tax'].create(tax_vals)
    
    def _create_fiscal_year(self):
        """Create fiscal year with periods"""
        fiscal_year = self.env['account.fiscal.year'].create({
            'name': f'Geschäftsjahr {self.fiscal_year_start.year}',
            'code': str(self.fiscal_year_start.year),
            'date_from': self.fiscal_year_start,
            'date_to': self.fiscal_year_end,
            'company_id': self.company_id.id,
            'state': 'open',
        })
        return fiscal_year
    
    def _migrate_existing_entries(self):
        """Migrate existing accounting entries to new accounts"""
        # Map old accounts to new SKR49 accounts
        mapping = {
            # This would contain actual mapping logic
            # For now, just a placeholder
        }
        
        # Find and update account move lines
        move_lines = self.env['account.move.line'].search([
            ('company_id', '=', self.company_id.id)
        ])
        
        for line in move_lines:
            # Apply mapping logic here
            pass