#!/bin/bash

echo "Deploying Kanban fix to Kulturhaus server..."
echo ""
echo "Password: [REMOVED - USE SSH KEY]"
echo ""

# sshpass removed - use SSH key authentication ssh khaus@v2202411240735294743.luckysrv.de << 'EOF'
echo "Pulling latest changes from GitHub..."
cd /opt/kulturhaus-docs
git pull origin main

echo "Deploying module..."
sudo cp -r addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions

echo "Restarting Odoo..."
sudo systemctl restart odoo18

echo "Updating module..."
sudo -u odoo18 /opt/odoo18/odoo-bin -d kulturhive -c /etc/odoo18.conf --update kulturhaus_board_resolutions --stop-after-init

echo "Final restart..."
sudo systemctl restart odoo18

echo "Done! Kanban view should now work."
EOF