#!/usr/bin/env python3
import sys
sys.path.insert(0, '/opt/odoo18/odoo')

import odoo
from odoo import api, SUPERUSER_ID

odoo.tools.config.parse_config(['-c', '/etc/odoo18.conf', '-d', 'kulturhive'])

with odoo.registry('kulturhive').cursor() as cr:
    env = api.Environment(cr, SUPERUSER_ID, {})
    
    # Update module list
    env['ir.module.module'].update_list()
    
    # Find and install module
    module = env['ir.module.module'].search([('name', '=', 'smart_notification')])
    if module:
        print(f"Found module: {module.name} - State: {module.state}")
        if module.state != 'installed':
            module.button_immediate_install()
            print("Module installation triggered!")
        else:
            print("Module already installed")
    else:
        print("Module not found in list")
    
    cr.commit()
    print("Done!")
