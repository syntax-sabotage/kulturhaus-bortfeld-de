#!/bin/bash

# Deployment script for Kulturhaus Board Resolution module
# Note: Password authentication is temporarily maintained per user decision

echo "Deploying to Kulturhaus server..."

# SSH with password (risk accepted by user)
sshpass -p 'Basf1$Khaus' ssh khaus@v2202411240735294743.luckysrv.de << 'EOF'
echo "Pulling latest changes from GitHub..."
cd /opt/kulturhaus-docs
git pull origin main

echo "Deploying module..."
sudo cp -r addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions

echo "Restarting Odoo..."
sudo systemctl restart odoo18

echo "Done! Deployment complete."
EOF