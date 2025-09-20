# -*- coding: utf-8 -*-
{
    'name': 'Smart Notification',
    'version': '18.2.1.0.0',
    'category': 'Productivity/Discuss',
    'summary': 'Intelligent global notification preferences for Odoo',
    'description': """
Smart Notification - Intelligent Global Notification Management
================================================================

Take control of your Odoo notifications with user-configurable global preferences.

Key Features:
-------------
* Global notification defaults per user
* Quick notification profiles (Minimal, Normal, Manager, Board)
* Per-model granular control
* Override capability for specific records
* Zero impact on Odoo core

© 2024 Syntax & Sabotage - Premium Odoo Solutions
    """,
    'author': 'Syntax & Sabotage',
    'website': 'https://www.syntaxandsabotage.io',
    'support': 'info@syntaxandsabotage.io',
    'license': 'OPL-1',
    'price': 199.00,
    'currency': 'EUR',
    'depends': [
        'base',
        'mail',
        'project',
    ],
    'data': [
        # Security
        'security/ir.model.access.csv',
        
        # Data
        'data/notification_profiles.xml',
        
        # Views
        'views/res_users_views.xml',
        'views/notification_profile_views.xml',
        'views/menu_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    
    # Odoo Store metadata
    'maintainer': 'Syntax & Sabotage',
    'contributors': [
        'Syntax & Sabotage <info@syntaxandsabotage.io>',
    ],
}