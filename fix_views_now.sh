#!/bin/bash

echo "=== FIXING BOARD RESOLUTION VIEWS ==="
echo ""
echo "This will remove the duplicate module from custom-addons and fix the views."
echo ""

# SSH connection details
SSH_HOST="v2202411240735294743.luckysrv.de"
SSH_USER="khaus"

# Create and execute remote commands
cat << 'REMOTE_COMMANDS' | ssh $SSH_USER@$SSH_HOST 'bash -s'

echo "Step 1: Checking for duplicate in custom-addons..."
if [ -d "/opt/odoo18/custom-addons/kulturhaus_board_resolutions" ]; then
    echo "✗ Found duplicate module in /opt/odoo18/custom-addons/"
    echo "  Removing it now..."
    sudo rm -rf /opt/odoo18/custom-addons/kulturhaus_board_resolutions
    echo "✓ Duplicate removed!"
else
    echo "✓ No duplicate found in custom-addons"
fi

echo ""
echo "Step 2: Updating the correct module in /opt/odoo18/odoo/addons/..."

# Clone or update the repository
if [ ! -d "/opt/kulturhaus-docs" ]; then
    echo "Cloning repository..."
    cd /opt
    sudo git clone https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git kulturhaus-docs
    sudo chown -R khaus:khaus /opt/kulturhaus-docs
else
    echo "Updating repository..."
    cd /opt/kulturhaus-docs
    git pull origin main
fi

# Deploy the latest version
echo "Deploying module..."
sudo rm -rf /opt/odoo18/odoo/addons/kulturhaus_board_resolutions
sudo cp -r /opt/kulturhaus-docs/addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions

echo ""
echo "Step 3: Cleaning database views..."
sudo -u postgres psql -d kulturhive << EOF
-- Remove any auto-generated broken views
DELETE FROM ir_ui_view 
WHERE model = 'board.resolution' 
AND (name LIKE '%auto%' OR name LIKE '%.auto%' OR arch_fs IS NULL);

-- Force module update
UPDATE ir_module_module 
SET state = 'to upgrade' 
WHERE name = 'kulturhaus_board_resolutions';

-- Show remaining views
SELECT name, priority FROM ir_ui_view 
WHERE model = 'board.resolution' 
ORDER BY priority;
EOF

echo ""
echo "Step 4: Clearing Python cache..."
sudo find /opt/odoo18/odoo/addons/kulturhaus_board_resolutions -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "Step 5: Restarting Odoo..."
sudo systemctl restart odoo18
sleep 10

echo ""
echo "Step 6: Forcing module update..."
sudo -u odoo18 /opt/odoo18/odoo-bin \
    -d kulturhive \
    -c /etc/odoo18.conf \
    --update kulturhaus_board_resolutions \
    --stop-after-init

echo ""
echo "Step 7: Final restart..."
sudo systemctl restart odoo18

echo ""
echo "=== ✓ FIX COMPLETE ==="
echo ""
echo "The duplicate module has been removed from custom-addons."
echo "The correct module in /opt/odoo18/odoo/addons/ has been updated."
echo "Board resolution views should now work properly!"
echo ""
echo "Test it: Open Vorstandsbeschlüsse and click on any resolution."

REMOTE_COMMANDS