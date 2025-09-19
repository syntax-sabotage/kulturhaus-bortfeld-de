#!/bin/bash

echo "=== DEPLOYING KANBAN VIEW FIX ==="
echo ""
echo "This will fix the 'Missing card template' error in the Kanban view."
echo ""

# Create and execute remote commands
cat << 'REMOTE_COMMANDS' | ssh kulturhaus 'bash -s'

echo "Step 1: Pulling latest changes from GitHub..."
cd /opt/kulturhaus-docs
git pull origin main

echo ""
echo "Step 2: Deploying the fixed module..."
sudo rm -rf /opt/odoo18/odoo/addons/kulturhaus_board_resolutions
sudo cp -r addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions

echo ""
echo "Step 3: Clearing Python cache..."
sudo find /opt/odoo18/odoo/addons/kulturhaus_board_resolutions -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

echo ""
echo "Step 4: Restarting Odoo..."
sudo systemctl restart odoo18
sleep 5

echo ""
echo "Step 5: Forcing module update..."
sudo -u odoo18 /opt/odoo18/odoo-bin \
    -d kulturhive \
    -c /etc/odoo18.conf \
    --update kulturhaus_board_resolutions \
    --stop-after-init

echo ""
echo "Step 6: Final restart..."
sudo systemctl restart odoo18

echo ""
echo "=== ✓ KANBAN FIX DEPLOYED ==="
echo ""
echo "The Kanban view template has been fixed!"
echo "The 'Missing card template' error should now be resolved."
echo ""
echo "Please refresh your browser and try the Kanban view again."

REMOTE_COMMANDS