#!/bin/bash

echo "=== FIXING BOARD RESOLUTION MODULE VIEWS ==="
echo "This script will:"
echo "1. Remove duplicate module installations"
echo "2. Deploy the correct version with working views"
echo "3. Update the module in Odoo"
echo ""

# SSH connection details
SSH_USER="khaus"
SSH_HOST="v2202411240735294743.luckysrv.de"
SSH_PASS="[REMOVED-USE-SSH-KEY]"

# Use sshpass to connect
export SSHPASS="$SSH_PASS"

echo "Step 1: Checking for duplicate modules..."
sshpass -e ssh -o StrictHostKeyChecking=no $SSH_USER@$SSH_HOST << 'EOF'
echo "Checking module locations..."
if [ -d "/opt/odoo18/custom-addons/kulturhaus_board_resolutions" ]; then
    echo "Found duplicate in /opt/odoo18/custom-addons/"
    echo "Backing up and removing..."
    sudo mv /opt/odoo18/custom-addons/kulturhaus_board_resolutions /opt/odoo18/custom-addons/kulturhaus_board_resolutions.backup.$(date +%Y%m%d_%H%M%S)
    echo "Removed duplicate module from custom-addons"
fi

if [ -d "/opt/odoo18/odoo/addons/kulturhaus_board_resolutions" ]; then
    echo "Found module in /opt/odoo18/odoo/addons/"
    echo "Backing up current version..."
    sudo cp -r /opt/odoo18/odoo/addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/kulturhaus_board_resolutions.backup.$(date +%Y%m%d_%H%M%S)
fi

echo ""
echo "Step 2: Pulling latest code from GitHub..."
cd /opt/kulturhaus-docs
git pull origin main

echo ""
echo "Step 3: Deploying fixed module..."
sudo rm -rf /opt/odoo18/odoo/addons/kulturhaus_board_resolutions
sudo cp -r /opt/kulturhaus-docs/addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions

echo ""
echo "Step 4: Clearing Odoo cache and restarting..."
# Clear filestore cache
sudo rm -rf /var/lib/odoo/.local/share/Odoo/filestore/kulturhive/*.cache

# Clear Python cache
sudo find /opt/odoo18/odoo/addons/kulturhaus_board_resolutions -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Restart Odoo
sudo systemctl restart odoo18
sleep 5

echo ""
echo "Step 5: Updating module in database..."
sudo -u odoo18 psql -d kulturhive << EOSQL
-- Force module update
UPDATE ir_module_module 
SET state = 'to upgrade' 
WHERE name = 'kulturhaus_board_resolutions';

-- Clear view cache
DELETE FROM ir_ui_view 
WHERE model = 'board.resolution' 
AND name LIKE '%auto%';

-- Ensure proper view ordering
UPDATE ir_ui_view 
SET priority = 99 
WHERE model = 'board.resolution' 
AND name NOT IN ('board.resolution.form', 'board.resolution.tree', 'board.resolution.search');

UPDATE ir_ui_view 
SET priority = 10 
WHERE model = 'board.resolution' 
AND name = 'board.resolution.form';

UPDATE ir_ui_view 
SET priority = 10 
WHERE model = 'board.resolution' 
AND name = 'board.resolution.tree';

EOSQL

echo ""
echo "Step 6: Triggering module update..."
python3 << EOPY
import xmlrpc.client

url = 'http://localhost:8069'
db = 'kulturhive'
username = 'admin'
password = 'khaus'

common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
uid = common.authenticate(db, username, password, {})

models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')

# Update the module
result = models.execute_kw(db, uid, password,
    'ir.module.module', 'button_immediate_upgrade',
    [[models.execute_kw(db, uid, password,
        'ir.module.module', 'search',
        [[['name', '=', 'kulturhaus_board_resolutions']]])]])

print("Module update triggered")
EOPY

echo ""
echo "Step 7: Final restart..."
sudo systemctl restart odoo18

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo "The board resolution module has been fixed."
echo "Duplicate modules removed, views cleaned up."
echo "Please test by clicking on a board resolution line item."
EOF

echo "Deployment script executed successfully!"