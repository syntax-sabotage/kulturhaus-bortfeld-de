#!/usr/bin/env python3
"""
Script to load demo data for kulturhaus_membership_sepa module
"""

import xmlrpc.client
import sys

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
    
    # Check if module is installed
    module = models.execute_kw(db, uid, password,
        'ir.module.module', 'search_read',
        [[['name', '=', 'kulturhaus_membership_sepa']]],
        {'fields': ['state', 'demo']})
    
    if not module:
        print("Module 'kulturhaus_membership_sepa' not found. Please install it first.")
        sys.exit(1)
    
    module_state = module[0]['state']
    has_demo = module[0].get('demo', False)
    
    print(f"Module state: {module_state}")
    print(f"Demo data loaded: {has_demo}")
    
    if module_state == 'installed':
        print("\nModule is installed. To load demo data:")
        print("1. Go to Apps menu in Odoo")
        print("2. Search for 'Kulturhaus Membership SEPA'")
        print("3. Click on the module")
        print("4. Click 'Upgrade' button")
        print("5. Make sure 'Load demonstration data' is checked in Settings > General Settings")
        
        # Try to count existing SEPA members
        partner_count = models.execute_kw(db, uid, password,
            'res.partner', 'search_count',
            [[['is_company', '=', False], ['sepa_mandate_id', '!=', False]]])
        
        print(f"\nCurrent SEPA members in database: {partner_count}")
        
    else:
        print(f"Module needs to be installed first. Current state: {module_state}")
        
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)