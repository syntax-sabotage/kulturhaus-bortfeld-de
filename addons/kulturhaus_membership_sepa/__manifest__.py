# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Membership SEPA',
    'version': '1.0.0',
    'category': 'Membership',
    'summary': 'SEPA payment management for Kulturhaus memberships',
    'description': """
        Kulturhaus Membership SEPA Module
        ==================================
        - SEPA mandate management for members
        - Configurable membership periods (full year/half year)
        - Manual batch generation with buttons
        - SEPA XML export for bank processing
    """,
    'author': 'Kulturhaus Bortfeld',
    'depends': ['base', 'membership', 'account', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'wizards/sepa_batch_wizard_views.xml',
        'views/res_partner_views.xml',
        'views/membership_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}