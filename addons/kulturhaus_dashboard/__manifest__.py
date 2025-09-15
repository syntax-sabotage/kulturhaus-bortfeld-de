# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Dashboard',
    'version': '1.0.0',
    'category': 'Productivity',
    'summary': 'Simplified card-based dashboard for Kulturhaus Bortfeld e.V.',
    'description': """
Kulturhaus Dashboard
==================

A mobile-optimized, card-based dashboard that provides simplified access to core business functions
for board members of Kulturhaus Bortfeld e.V.

Key Features:
* Card-based navigation interface
* Mobile-first responsive design
* User preference toggle (optional dashboard)
* 3 KPI widgets for quick insights
* Configurable card layout and themes
* Non-invasive integration with existing Odoo

Target Users:
* Board members
* Event coordinators  
* Non-technical users requiring simplified navigation

The dashboard can be enabled per user and provides an alternative to the standard Odoo interface
while preserving all existing functionality.
""",
    'author': 'Kulturhaus Bortfeld e.V.',
    'website': 'https://kulturhaus-bortfeld.de',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'web',
        'website',
        'event',
        'kulturhaus_membership_sepa',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/dashboard_final.xml',
        'views/instagram_config_views.xml',
        'views/instagram_complete_views.xml',
    ],
    'assets': {
    },
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 100,
    'external_dependencies': {
        'python': [],
    },
}