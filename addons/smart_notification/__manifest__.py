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
* Bulk application to existing followers
* Zero impact on Odoo core

Perfect for:
------------
* Organizations with board members who need everything
* Teams wanting to reduce notification fatigue
* Users who want consistent notification behavior
* Enterprises needing scalable notification management

How it Works:
-------------
1. Configure your preferences once in your user profile
2. Every record you follow uses YOUR preferences automatically
3. Override per-record when needed
4. No more manual configuration for each follow!

Technical Excellence:
--------------------
* Native Odoo architecture integration
* Performance optimized with caching
* Fully compatible with Odoo 18
* Enterprise-ready code quality
* Comprehensive test coverage

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
        'security/security.xml',
        
        # Data
        'data/notification_profiles.xml',
        
        # Views
        'views/res_users_views.xml',
        'views/notification_profile_views.xml',
        'views/menu_views.xml',
        
        # Wizards
        'wizard/apply_preferences_wizard_views.xml',
    ],
    'demo': [
        'demo/demo_profiles.xml',
    ],
    'images': [
        'static/description/banner.png',
        'static/description/icon.png',
        'static/description/screenshot_1.png',
        'static/description/screenshot_2.png',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'post_init_hook': 'post_init_hook',
    
    # Odoo Store metadata
    'maintainer': 'Syntax & Sabotage',
    'contributors': [
        'Syntax & Sabotage <info@syntaxandsabotage.io>',
    ],
}