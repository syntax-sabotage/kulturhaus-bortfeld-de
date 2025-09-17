# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus Calendar Subscription',
    'version': '1.0.0',
    'category': 'Productivity/Calendar',
    'summary': 'Subscribe to Odoo calendars via iCal feeds',
    'description': """
Kulturhaus Calendar Subscription Module
=======================================

This module allows users to generate secure subscription URLs for their Odoo calendars,
compatible with Apple Calendar, Google Calendar, Outlook, and other iCal clients.

Key Features:
-------------
* Secure token-based authentication
* Read-only calendar feeds
* Configurable privacy settings
* Usage tracking and monitoring
* Multiple subscriptions per user
* Odoo 18 compatible

Technical Details:
------------------
* Uses icalendar library for proper iCal formatting
* Implements webcal:// protocol support
* Provides HTTP caching headers for efficiency
* Timezone-aware event handling
    """,
    'author': 'Kulturhaus Bortfeld',
    'website': 'https://kulturhaus-bortfeld.de',
    'depends': ['base', 'calendar'],
    'external_dependencies': {
        'python': ['icalendar'],
    },
    'data': [
        'security/ir.model.access.csv',
        'security/calendar_subscription_security.xml',
        'views/calendar_subscription_views.xml',
        'views/res_users_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}