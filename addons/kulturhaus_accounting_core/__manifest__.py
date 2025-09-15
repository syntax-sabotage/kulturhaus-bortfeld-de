# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Accounting Core',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'SKR49 Kontenrahmen für gemeinnützige Vereine',
    'description': """
        Kulturhaus Accounting Core
        ===========================
        Grundlegendes Buchhaltungsmodul für Kulturhaus Bortfeld e.V.
        
        Funktionen:
        -----------
        * SKR49 Kontenrahmen für gemeinnützige Vereine
        * Deutsche Steuerkonfiguration (0%, 7%, 19%)
        * Geschäftsjahre und Perioden
        * Kontenzuordnung und Migration
        * Spezielle Vereinskonten
    """,
    'author': 'Kulturhaus Bortfeld e.V.',
    'website': 'https://kulturhaus-bortfeld.de',
    'depends': ['account', 'l10n_de'],
    'data': [
        'security/ir.model.access.csv',
        'data/account_chart_template.xml',
        'data/account_tax_template.xml',
        'data/account_fiscal_position.xml',
        'views/account_views.xml',
        'views/menu_views.xml',
        'wizard/account_setup_wizard_views.xml',
    ],
    'demo': [
        'demo/demo_data.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
    'post_init_hook': 'post_init_hook',
}