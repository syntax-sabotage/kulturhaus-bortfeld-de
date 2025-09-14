#!/usr/bin/env python3
"""
Script to upgrade kulturhaus_membership_sepa module with demo data
"""

import xmlrpc.client
import sys
import time

# Odoo connection parameters
url = 'http://localhost:8070'
db = 'kulturhaus_dev'
username = 'admin'
password = 'admin'

try:
    # Connect to Odoo
    common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
    uid = common.authenticate(db, username, password, {})
    
    if not uid:
        print("Authentication failed. Please check credentials.")
        sys.exit(1)
    
    print(f"Connected to Odoo as user ID: {uid}")
    
    # Get the models object
    models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
    
    # First, enable demo data in the system
    print("Enabling demo data in system settings...")
    config_param = models.execute_kw(db, uid, password,
        'ir.config_parameter', 'set_param',
        ['demo', 'True'])
    
    # Find the module
    module = models.execute_kw(db, uid, password,
        'ir.module.module', 'search',
        [[['name', '=', 'kulturhaus_membership_sepa']]])
    
    if not module:
        print("Module 'kulturhaus_membership_sepa' not found.")
        sys.exit(1)
    
    module_id = module[0]
    print(f"Found module ID: {module_id}")
    
    # Set the module to upgrade state
    print("Setting module to upgrade state...")
    models.execute_kw(db, uid, password,
        'ir.module.module', 'button_immediate_upgrade',
        [[module_id]])
    
    print("Module upgrade initiated. Waiting for completion...")
    time.sleep(5)
    
    # Check the results
    partner_count = models.execute_kw(db, uid, password,
        'res.partner', 'search_count',
        [[['is_company', '=', False], ['sepa_mandate_id', '!=', False]]])
    
    print(f"\n✓ Module upgraded successfully!")
    print(f"✓ SEPA members with mandates in database: {partner_count}")
    
    if partner_count > 0:
        # Get a sample of the loaded members
        sample_partners = models.execute_kw(db, uid, password,
            'res.partner', 'search_read',
            [[['is_company', '=', False], ['sepa_mandate_id', '!=', False]]],
            {'fields': ['name', 'sepa_mandate_id', 'sepa_iban', 'sepa_bic'], 'limit': 5})
        
        print("\nSample of loaded demo members:")
        for partner in sample_partners:
            print(f"  - {partner['name']}: IBAN={partner.get('sepa_iban', 'N/A')}, "
                  f"Mandate={partner.get('sepa_mandate_id', 'N/A')}")
    
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)