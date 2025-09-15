# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Spendenbescheinigungen',
    'version': '18.0.1.0.0',
    'category': 'Accounting',
    'summary': 'Zuwendungsbescheinigungen nach deutschem Recht',
    'description': """
        Kulturhaus Spendenbescheinigungen
        ==================================
        Erstellung von Zuwendungsbescheinigungen für deutsche gemeinnützige Vereine
        
        Funktionen:
        -----------
        * BMF-konforme Zuwendungsbescheinigungen
        * Unterscheidung Geld-/Sachspenden
        * Unterscheidung Spenden/Mitgliedsbeiträge
        * Sammelbestätigungen
        * Automatischer Jahresversand
        * QR-Code für Finanzamt
    """,
    'author': 'Kulturhaus Bortfeld e.V.',
    'website': 'https://kulturhaus-bortfeld.de',
    'depends': [
        'account',
        'contacts',
        'kulturhaus_accounting_core',
    ],
    'data': [
        'security/ir.model.access.csv',
        'data/donation_sequence.xml',
        'report/donation_certificate_template.xml',
        'report/donation_certificate_report.xml',
        'views/donation_certificate_views.xml',
        'views/res_partner_views.xml',
        'views/menu_views.xml',
        'wizard/donation_certificate_wizard_views.xml',
        'wizard/annual_certificate_wizard_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
    'license': 'LGPL-3',
}