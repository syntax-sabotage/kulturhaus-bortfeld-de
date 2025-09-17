# -*- coding: utf-8 -*-
{
    'name': 'KH Menu Organizer',
    'version': '1.0.0',
    'category': 'Tools',
    'summary': 'Organize Odoo menus with drag-drop reordering',
    'description': """
KH Menu Organizer
=================

This module allows you to organize your Odoo main menu:
- Drag and drop to reorder menu items
- Assign categories to group related menus
- Add separator markers (for future theme customization)
- Hide menus temporarily

Simple and safe menu organization tool.
    """,
    'author': 'Kulturhaus Bortfeld',
    'website': 'https://kulturhaus-bortfeld.de',
    'license': 'LGPL-3',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/menu_organizer_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}