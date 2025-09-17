# -*- coding: utf-8 -*-
{
    'name': 'Kulturhaus German Checkout',
    'version': '14.0',
    'category': 'Website/eCommerce',
    'summary': 'German checkout with proper button styling',
    'description': '''
German checkout improvements:
- Green instruction box with step-by-step guidance
- Zur Kasse gehen button: GREEN (primary action)
- Confirm Order button: GREY (secondary styling)
- German translations for better UX
    ''',
    'author': 'Kulturhaus Bortfeld e.V.',
    'depends': ['website_sale', 'payment'],
    'data': [
        'views/checkout_templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'license': 'LGPL-3',
}
