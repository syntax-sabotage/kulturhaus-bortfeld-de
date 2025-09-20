#!/bin/bash

# Deployment script for board resolution translations
echo "Deploying board resolution translations..."

# Server details
SERVER="kulturhaus"
ADDON_PATH="/opt/odoo18/odoo/addons/kulturhaus_board_resolutions"

# Copy fixed Python model with translation markers
echo "1. Copying fixed meeting_type.py..."
scp meeting_type_fixed.py $SERVER:$ADDON_PATH/models/meeting_type.py

# Copy fixed view files
echo "2. Copying fixed view files..."
scp meeting_type_views_fixed.xml $SERVER:$ADDON_PATH/views/meeting_type_views.xml
scp board_resolution_views_fixed.xml $SERVER:$ADDON_PATH/views/board_resolution_views.xml

# Create i18n directory if it doesn't exist
echo "3. Creating i18n directory..."
ssh $SERVER "sudo mkdir -p $ADDON_PATH/i18n"

# Copy German translation file
echo "4. Copying German translation file..."
scp de_full_v3.po $SERVER:$ADDON_PATH/i18n/de_DE.po

# Copy complete translation files
echo "5. Copying additional translation files..."
scp de_complete_v2.po $SERVER:$ADDON_PATH/i18n/de.po

# Fix permissions
echo "6. Fixing permissions..."
ssh $SERVER "sudo chown -R odoo18:odoo18 $ADDON_PATH"

# Restart Odoo
echo "7. Restarting Odoo..."
ssh $SERVER "sudo systemctl restart odoo18"

echo "Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Go to Odoo interface"
echo "2. Apps menu -> Update App List"
echo "3. Search for 'Board Resolutions' and upgrade the module"
echo "4. Go to Settings -> Users & Companies -> Users"
echo "5. Edit your user and set Language to Deutsch (German)"
echo "6. Refresh browser to see German interface"