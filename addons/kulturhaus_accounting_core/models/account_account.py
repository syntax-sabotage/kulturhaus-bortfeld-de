# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class AccountAccount(models.Model):
    _inherit = 'account.account'
    
    skr49_code = fields.Char(
        string='SKR49 Code',
        help='Kontonummer nach SKR49 für gemeinnützige Vereine'
    )
    
    is_nonprofit_account = fields.Boolean(
        string='Gemeinnütziges Konto',
        help='Markiert Konten, die speziell für gemeinnützige Zwecke verwendet werden'
    )
    
    nonprofit_type = fields.Selection([
        ('donation', 'Spendenkonto'),
        ('membership', 'Mitgliedsbeiträge'),
        ('grant', 'Zuschüsse/Förderungen'),
        ('event', 'Veranstaltungserlöse'),
        ('economic', 'Wirtschaftlicher Geschäftsbetrieb'),
        ('purpose', 'Zweckbetrieb'),
        ('asset_mgmt', 'Vermögensverwaltung'),
    ], string='Vereinskontentyp')
    
    tax_deductible = fields.Boolean(
        string='Steuerlich absetzbar',
        help='Markiert Konten für steuerlich absetzbare Einnahmen'
    )
    
    @api.model
    def create_skr49_accounts(self):
        """Create SKR49 standard accounts for non-profit organizations"""
        accounts_data = [
            # Aktiva
            {'code': '0100', 'name': 'Kasse', 'account_type': 'asset_cash'},
            {'code': '1200', 'name': 'Bankkonten', 'account_type': 'asset_cash'},
            {'code': '1400', 'name': 'Forderungen aus Lieferungen und Leistungen', 'account_type': 'asset_receivable'},
            
            # Passiva
            {'code': '2000', 'name': 'Eigenkapital', 'account_type': 'equity'},
            {'code': '2100', 'name': 'Rücklagen', 'account_type': 'equity'},
            {'code': '3000', 'name': 'Verbindlichkeiten aus Lieferungen und Leistungen', 'account_type': 'liability_payable'},
            
            # Erträge - Ideeller Bereich
            {'code': '4000', 'name': 'Mitgliedsbeiträge', 'account_type': 'income', 'nonprofit_type': 'membership'},
            {'code': '4100', 'name': 'Spenden', 'account_type': 'income', 'nonprofit_type': 'donation', 'tax_deductible': True},
            {'code': '4200', 'name': 'Zuschüsse und Zuwendungen', 'account_type': 'income', 'nonprofit_type': 'grant'},
            
            # Erträge - Zweckbetrieb
            {'code': '4300', 'name': 'Erlöse Zweckbetrieb', 'account_type': 'income', 'nonprofit_type': 'purpose'},
            {'code': '4400', 'name': 'Veranstaltungserlöse', 'account_type': 'income', 'nonprofit_type': 'event'},
            
            # Erträge - Wirtschaftlicher Geschäftsbetrieb
            {'code': '4500', 'name': 'Erlöse wirtschaftlicher Geschäftsbetrieb', 'account_type': 'income', 'nonprofit_type': 'economic'},
            
            # Aufwendungen
            {'code': '6000', 'name': 'Personalaufwand', 'account_type': 'expense'},
            {'code': '6100', 'name': 'Raumkosten', 'account_type': 'expense'},
            {'code': '6200', 'name': 'Veranstaltungskosten', 'account_type': 'expense'},
            {'code': '6300', 'name': 'Verwaltungskosten', 'account_type': 'expense'},
            {'code': '6400', 'name': 'Werbe- und Reisekosten', 'account_type': 'expense'},
            {'code': '6500', 'name': 'Sonstige betriebliche Aufwendungen', 'account_type': 'expense'},
            
            # Steuerkonten
            {'code': '1571', 'name': 'Abziehbare Vorsteuer 7%', 'account_type': 'asset_current'},
            {'code': '1576', 'name': 'Abziehbare Vorsteuer 19%', 'account_type': 'asset_current'},
            {'code': '3801', 'name': 'Umsatzsteuer 7%', 'account_type': 'liability_current'},
            {'code': '3806', 'name': 'Umsatzsteuer 19%', 'account_type': 'liability_current'},
        ]
        
        for account_data in accounts_data:
            existing = self.search([
                ('code', '=', account_data['code']),
                ('company_id', '=', self.env.company.id)
            ])
            if not existing:
                account_data.update({
                    'skr49_code': account_data['code'],
                    'is_nonprofit_account': True,
                    'company_id': self.env.company.id,
                })
                self.create(account_data)
        
        return True