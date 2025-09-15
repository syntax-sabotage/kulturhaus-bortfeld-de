#!/usr/bin/env python3
import xmlrpc.client

# Odoo connection details
url = 'http://localhost:8070'
db = 'kulturhaus_dev'
username = 'admin'
password = 'admin'

# Facebook Access Token
access_token = """EAAP9pKO2cIoBPYsts3Q1sezJXEV3faVaQ9LdXl3lMsw29l6xjYQrmeYt2DEypC7Ob6B0ZAoQ3R8wQfWpf3F9ZCDxE5tZBtPhNLx9LGw5OQmOZAZAgfxb3YoUXijOwtPKZCReYySQzv5mk1c0b6MLmQpZBCbf1NyZACrZAFDngBPawFatTMMbA6AlKKI5BosTDcNqI"""

# Connect to Odoo
common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})
models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Search for existing Instagram config
config_ids = models.execute_kw(db, uid, password,
    'kulturhaus.instagram.config', 'search', [[]])

if config_ids:
    # Update existing config
    models.execute_kw(db, uid, password,
        'kulturhaus.instagram.config', 'write', 
        [config_ids, {
            'facebook_app_id': '1123308493238410',
            'facebook_app_secret': '802d2f3001db751111487afef63207f5',
            'facebook_access_token': access_token,
            'api_connected': True
        }])
    print(f"Token saved to config ID: {config_ids[0]}")
else:
    # Create new config
    config_id = models.execute_kw(db, uid, password,
        'kulturhaus.instagram.config', 'create', [{
            'account_name': 'kulturhaus_bortfeld',
            'facebook_app_id': '1123308493238410',
            'facebook_app_secret': '802d2f3001db751111487afef63207f5',
            'facebook_access_token': access_token,
            'api_connected': True,
            'instagram_business_id': '17841464815983915'
        }])
    print(f"Created new config with ID: {config_id}")

print("Token saved successfully!")
print("\nÖffne: http://localhost:8070")
print("Gehe zu: Dashboard → Instagram Configuration")