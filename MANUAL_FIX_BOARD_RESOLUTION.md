# Manual Fix for Board Resolution Views

## Problem
When clicking on a board resolution line item, a broken/empty view opens instead of the proper form view. This is caused by duplicate module installations in two locations.

## Solution Steps

### 1. Connect to Server
```bash
ssh khaus@v2202411240735294743.luckysrv.de
# Password: Basf1$Khaus
```

### 2. Remove Duplicate Module (CRITICAL STEP)
```bash
# Check if duplicate exists in custom-addons (THIS IS THE WRONG LOCATION)
ls -la /opt/odoo18/custom-addons/kulturhaus_board_resolutions

# If it exists, REMOVE IT - it doesn't belong there:
sudo rm -rf /opt/odoo18/custom-addons/kulturhaus_board_resolutions

# This removes the conflicting duplicate that's causing the broken views
# The correct module stays in /opt/odoo18/odoo/addons/ where ALL your modules are
```

### 3. Update Main Module
```bash
# Clone or update repository
cd /opt
if [ ! -d "kulturhaus-docs" ]; then
    sudo git clone https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git kulturhaus-docs
fi

cd /opt/kulturhaus-docs
git pull origin main

# Deploy the fixed module
sudo rm -rf /opt/odoo18/odoo/addons/kulturhaus_board_resolutions
sudo cp -r /opt/kulturhaus-docs/addons/kulturhaus_board_resolutions /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_board_resolutions
```

### 4. Clean Database Views
```bash
# Connect to database
sudo -u postgres psql -d kulturhive

# Run these SQL commands:
```
```sql
-- Remove auto-generated broken views
DELETE FROM ir_ui_view 
WHERE model = 'board.resolution' 
AND name LIKE '%auto%';

-- Set module to upgrade
UPDATE ir_module_module 
SET state = 'to upgrade' 
WHERE name = 'kulturhaus_board_resolutions';

-- Exit psql
\q
```

### 5. Clear Cache and Restart
```bash
# Clear Python cache
sudo find /opt/odoo18/odoo/addons/kulturhaus_board_resolutions -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Restart Odoo
sudo systemctl restart odoo18

# Wait 10 seconds
sleep 10
```

### 6. Update Module via CLI
```bash
# Force module update
sudo -u odoo18 /opt/odoo18/odoo-bin \
    -d kulturhive \
    -c /etc/odoo18.conf \
    --update kulturhaus_board_resolutions \
    --stop-after-init
```

### 7. Final Restart
```bash
sudo systemctl restart odoo18
```

## Verification

1. Open https://kulturhaus-bortfeld.de
2. Navigate to Vorstandsbeschlüsse 
3. Click on any board resolution line item
4. **Should now open the proper form view** with all fields and tabs visible

## What This Fixes

- ✅ Removes duplicate module from `/opt/odoo18/custom-addons/`
- ✅ Deploys correct version to `/opt/odoo18/odoo/addons/`
- ✅ Cleans up broken auto-generated views from database
- ✅ Ensures form view opens when clicking on resolutions

## Root Cause

The issue was caused by having the same module installed in two locations:
1. `/opt/odoo18/odoo/addons/kulturhaus_board_resolutions/` (CORRECT location - where ALL your modules are)
2. `/opt/odoo18/custom-addons/kulturhaus_board_resolutions/` (WRONG location - duplicate causing conflicts)

Both were being loaded by Odoo, creating conflicting view definitions. The broken views were being auto-generated when Odoo couldn't resolve the conflicts. The custom-addons folder should NOT contain this module.

## If Problem Persists

Check which views exist:
```sql
sudo -u postgres psql -d kulturhive -c "SELECT name, priority, arch_fs FROM ir_ui_view WHERE model = 'board.resolution' ORDER BY priority;"
```

The output should show:
- `board.resolution.form` (priority 1 or 10)
- `board.resolution.tree` (priority 10)
- `board.resolution.search` (priority 16)

No auto-generated views should exist.