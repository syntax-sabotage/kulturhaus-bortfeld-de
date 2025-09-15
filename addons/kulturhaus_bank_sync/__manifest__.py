# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Bank Synchronisation',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Bankdaten Import und automatische Abstimmung',
    'description': """
        Kulturhaus Bank Synchronisation
        ================================
        Automatisierte Bankdaten-Verarbeitung für Kulturhaus Bortfeld e.V.
        
        Funktionen:
        -----------
        * CSV und CAMT.053 Import
        * Automatische Zuordnung zu Stripe und SEPA Zahlungen
        * Regelbasierte Abstimmung
        * Verarbeitung unabgestimmter Posten
        * Bulk-Abstimmung
    """,
    'author': 'Kulturhaus Bortfeld e.V.',
    'website': 'https://kulturhaus-bortfeld.de',
    'depends': [
        'account',
        'account_accountant',
        'kulturhaus_accounting_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/reconciliation_rules.xml',
        'views/bank_sync_views.xml',
        'views/reconciliation_rule_views.xml',
        'views/menu_views.xml',
        'wizard/bank_import_wizard_views.xml',
        'wizard/bulk_reconcile_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}