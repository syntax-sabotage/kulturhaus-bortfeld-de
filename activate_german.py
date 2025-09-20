#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xmlrpc.client
import sys

# Odoo connection details
url = 'https://kulturhaus-bortfeld.de'
db = 'kulturhive'
username = 'admin'
password = 'khaus'

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

if not uid:
    print("Authentication failed!")
    sys.exit(1)

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

print("Connected to Odoo successfully!")

# Check if German language is installed
lang_ids = models.execute_kw(db, uid, password,
    'res.lang', 'search', 
    [[['code', '=', 'de_DE']]])

if not lang_ids:
    print("German language not found. Installing...")
    # Load German language
    wizard_id = models.execute_kw(db, uid, password,
        'base.language.install', 'create',
        [{'lang_ids': [(6, 0, [])], 'overwrite': True}])
    
    # Get available languages
    langs = models.execute_kw(db, uid, password,
        'res.lang', 'get_installed', [])
    
    print(f"Available languages: {langs}")
    
    # Install German
    wizard_vals = {
        'lang': 'de_DE',
        'overwrite': True
    }
    wizard_id = models.execute_kw(db, uid, password,
        'base.language.install', 'create', [wizard_vals])
    
    models.execute_kw(db, uid, password,
        'base.language.install', 'lang_install', [[wizard_id]])
    
    print("German language installed!")
else:
    lang = models.execute_kw(db, uid, password,
        'res.lang', 'read', [lang_ids, ['name', 'code', 'active']])
    print(f"German language found: {lang[0]}")
    
    # Activate if not active
    if not lang[0]['active']:
        print("Activating German language...")
        models.execute_kw(db, uid, password,
            'res.lang', 'write', 
            [lang_ids, {'active': True}])
        print("German language activated!")

# Update translations for the board resolutions module
print("\nUpdating translations for kulturhaus_board_resolutions module...")

# Find the module
module_ids = models.execute_kw(db, uid, password,
    'ir.module.module', 'search',
    [[['name', '=', 'kulturhaus_board_resolutions']]])

if module_ids:
    module = models.execute_kw(db, uid, password,
        'ir.module.module', 'read',
        [module_ids, ['state']])
    
    print(f"Module found in state: {module[0]['state']}")
    
    # Update translations
    try:
        models.execute_kw(db, uid, password,
            'ir.translation', 'load_module_terms',
            [['kulturhaus_board_resolutions'], ['de_DE']])
        print("Translations loaded!")
    except Exception as e:
        print(f"Error loading translations: {e}")
        print("Trying alternative method...")
        
        # Alternative: Sync translations
        trans_obj = models.execute_kw(db, uid, password,
            'base.update.translations', 'create',
            [{'lang': 'de_DE'}])
        
        models.execute_kw(db, uid, password,
            'base.update.translations', 'act_update',
            [[trans_obj]])
        
        print("Translation sync initiated!")

# Set German for admin user
print("\nSetting German language for admin user...")
admin_id = models.execute_kw(db, uid, password,
    'res.users', 'search',
    [[['login', '=', 'admin']]])

if admin_id:
    models.execute_kw(db, uid, password,
        'res.users', 'write',
        [admin_id, {'lang': 'de_DE'}])
    print("Admin user language set to German!")

print("\n✅ German localization setup complete!")
print("Please refresh your browser to see the changes.")