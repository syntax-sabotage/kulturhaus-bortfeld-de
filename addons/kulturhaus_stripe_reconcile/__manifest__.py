# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Stripe Abstimmung',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Automatische Stripe Zahlungsabstimmung',
    'description': """
        Kulturhaus Stripe Abstimmung
        =============================
        Automatische Abstimmung von Stripe Zahlungen
        
        Funktionen:
        -----------
        * Webhook Integration für Echtzeit-Updates
        * Automatische Zuordnung zu Rechnungen
        * Gebührenverarbeitung
        * Rückerstattungen
        * Zahlungsstatus-Tracking
        * Batch-Abstimmung
    """,
    'author': 'Kulturhaus Bortfeld e.V.',
    'website': 'https://kulturhaus-bortfeld.de',
    'depends': [
        'account',
        'payment',
        'website_payment',
        'kulturhaus_bank_sync',
    ],
    'external_dependencies': {
        'python': ['stripe'],
    },
    'data': [
        'security/ir.model.access.csv',
        'data/stripe_data.xml',
        'views/stripe_payment_views.xml',
        'views/account_move_views.xml',
        'views/res_config_settings_views.xml',
        'views/menu_views.xml',
        'wizard/stripe_sync_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}