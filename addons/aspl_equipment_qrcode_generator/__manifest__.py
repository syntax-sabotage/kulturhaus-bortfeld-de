# -*- coding: utf-8 -*-
###############################################################################
#
# Aspire Softserv Pvt. Ltd.
# Copyright (C) Aspire Softserv Pvt. Ltd.(<https://aspiresoftserv.com>).
#
###############################################################################
{
    "name": "QR Code on Equipment",
    'category': '',
    "summary": "Add QR Code on equipment for managing equipment.",
    "license": "LGPL-3",
    "price": 00.00,
    'description': """
        The Equipment Management Module generates unique QR codes for each asset, offering instant details and direct Odoo profile access for seamless management.
    """,
    "author": "Aspire Softserv Pvt. Ltd",
    "website": "https://aspiresoftserv.com",
    "depends": ['account','maintenance'],
    "external_dependencies": {
        'python': ['qrcode']
    },
    "data": [
        'views/maintenance_equipment.xml',
        'security/ir.model.access.csv',
        'report/custom_qrcode.xml',
        'wizard/equipment_label_layout_views.xml',
    ],
    'pre_init_hook': 'pre_init_hook',
    "application": True,
    "installable": True,
    "maintainer": "Aspire Softserv Pvt. Ltd",
    "support": "odoo@aspiresoftserv.com",
    'images': ['static/description/banner.gif'],
}
