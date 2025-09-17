########################################################################
#                                                                      #
#     ------------------------ODOO WAVES----------------------         #
#     --------------odoowaves.solution@gmail.com--------------         #
#                                                                      #
########################################################################
{
    "name": "Odoo Python Pip Installer",
    "summary": """Install The Library With In The Odoo Environment in easily, directly and better way""",
    "category": "Extra Tools",
    "sequence": 2,
    "author": "Odoo Waves",
    "license": "LGPL-3",
    "website": "",
    "description": """Python Library Installer""",
    "data": [
        'security/ir.model.access.csv',
        'views/menus.xml',
        'wizard/pip_command_view.xml',
        'wizard/message_wizard_view.xml'
    ],
    "images": ['static/description/banner.gif'],
    "application": True,
    "installable": True,
    "auto_install": False,

}
