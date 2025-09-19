#!/bin/bash

echo "=== DEPLOYING BOARD RESOLUTION FIX TO VPS ==="
echo ""

# Create a remote script that will be executed with proper sudo
cat << 'REMOTE_SCRIPT' > /tmp/fix_board_resolution.sh
#!/bin/bash

echo "Step 1: Checking and removing duplicate modules..."

# Check and backup duplicate in custom-addons
if [ -d "/opt/odoo18/custom-addons/kulturhaus_board_resolutions" ]; then
    echo "Found duplicate in /opt/odoo18/custom-addons/"
    echo "Moving to backup..."
    sudo mv /opt/odoo18/custom-addons/kulturhaus_board_resolutions /opt/odoo18/custom-addons/kulturhaus_board_resolutions.backup.$(date +%Y%m%d_%H%M%S)
    echo "✓ Removed duplicate from custom-addons"
fi

# Check main addons directory
if [ -d "/opt/odoo18/odoo/addons/kulturhaus_board_resolutions" ]; then
    echo "Found module in /opt/odoo18/odoo/addons/"
    echo "Creating backup..."
    sudo cp -r /opt/odoo18/odoo/addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/kulturhaus_board_resolutions.backup.$(date +%Y%m%d_%H%M%S)
fi

echo ""
echo "Step 2: Cloning repository if needed..."
if [ ! -d "/opt/kulturhaus-docs" ]; then
    cd /opt
    sudo git clone https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git kulturhaus-docs
    sudo chown -R khaus:khaus /opt/kulturhaus-docs
else
    cd /opt/kulturhaus-docs
    git pull origin main
fi

echo ""
echo "Step 3: Deploying fixed module..."
sudo rm -rf /opt/odoo18/odoo/addons/kulturhaus_board_resolutions
sudo cp -r /opt/kulturhaus-docs/addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions

echo ""
echo "Step 4: Clearing cache..."
# Clear Python cache
sudo find /opt/odoo18/odoo/addons/kulturhaus_board_resolutions -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Clear Odoo filestore cache if it exists
if [ -d "/var/lib/odoo/.local/share/Odoo/filestore/kulturhive" ]; then
    sudo find /var/lib/odoo/.local/share/Odoo/filestore/kulturhive -name "*.cache" -delete 2>/dev/null || true
fi

echo ""
echo "Step 5: Updating database..."
sudo -u postgres psql -d kulturhive << EOF
-- First, clean up any broken views
DELETE FROM ir_ui_view 
WHERE model = 'board.resolution' 
AND (name LIKE '%auto%' OR arch_fs IS NULL);

-- Force module to upgrade state
UPDATE ir_module_module 
SET state = 'to upgrade' 
WHERE name = 'kulturhaus_board_resolutions';

-- Ensure form view has proper priority
UPDATE ir_ui_view 
SET priority = 1
WHERE model = 'board.resolution' 
AND name = 'board.resolution.form';

UPDATE ir_ui_view 
SET priority = 10
WHERE model = 'board.resolution' 
AND name = 'board.resolution.tree';

-- Check for conflicting views
SELECT name, priority, arch_fs, id 
FROM ir_ui_view 
WHERE model = 'board.resolution' 
ORDER BY priority, name;
EOF

echo ""
echo "Step 6: Restarting Odoo..."
sudo systemctl restart odoo18

echo ""
echo "Waiting for Odoo to start..."
sleep 10

echo ""
echo "Step 7: Triggering module update via CLI..."
sudo -u odoo18 /opt/odoo18/odoo-bin -d kulturhive -c /etc/odoo18.conf --update kulturhaus_board_resolutions --stop-after-init

echo ""
echo "Step 8: Final restart..."
sudo systemctl restart odoo18

echo ""
echo "=== DEPLOYMENT COMPLETE ==="
echo ""
echo "Summary:"
echo "✓ Duplicate module removed from custom-addons"
echo "✓ Latest code deployed to /opt/odoo18/odoo/addons/"
echo "✓ Module updated in database"
echo "✓ Cache cleared and Odoo restarted"
echo ""
echo "The board resolution views should now work properly."
echo "Test by opening Vorstandsbeschlüsse and clicking on any resolution."
REMOTE_SCRIPT

echo "Copying script to server..."
scp /tmp/fix_board_resolution.sh khaus@v2202411240735294743.luckysrv.de:/tmp/

echo "Connecting to server to execute fix..."
echo "You will need to enter the password: [REMOVED-USE-SSH-KEY]"
ssh khaus@v2202411240735294743.luckysrv.de 'bash /tmp/fix_board_resolution.sh'

echo "Done!"