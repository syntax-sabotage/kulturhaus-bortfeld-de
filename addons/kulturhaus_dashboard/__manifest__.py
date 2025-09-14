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
        'event',
        'kulturhaus_membership_sepa',
    ],
    'data': [
        'security/groups.xml',
        'security/ir.model.access.csv',
        'data/dashboard_data.xml',
        'views/dashboard_proper_view.xml',
        'views/dashboard_view.xml',
        'views/dashboard_card_config_views.xml',
        'views/res_users_view.xml',
        'views/user_profile_views.xml',
        'views/menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'kulturhaus_dashboard/static/src/css/dashboard.css',
            'kulturhaus_dashboard/static/src/css/dashboard_mvp.css',
            'kulturhaus_dashboard/static/src/js/dashboard.js',
            'kulturhaus_dashboard/static/src/js/dashboard_simple.js',
            'kulturhaus_dashboard/static/src/js/dashboard_mvp_fixed.js',
            'kulturhaus_dashboard/static/src/xml/dashboard.xml',
            'kulturhaus_dashboard/static/src/xml/dashboard_mvp.xml',
        ],
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