# Session Handover - kulturhaus_board_resolutions Module

**Date**: 2025-01-18
**Status**: Module installed but wizard form empty
**Priority**: High - Fix wizard form display issue

## Current Situation

### ✅ Completed
1. **Module Installation**: kulturhaus_board_resolutions v18.2.1.0.0 successfully installed
2. **Odoo 18 Compatibility**: All compatibility issues fixed:
   - Version updated to 18.2.1.0.0
   - View types changed from `tree` to `list`
   - Attributes migrated from `attrs` to direct syntax
   - Menu loading order corrected
   - Demo data removed
3. **Security Fix**: Database manager exposure fixed in /etc/odoo18.conf
4. **Board Member Functionality**: Checkbox added to contacts (after Position field)
5. **Menu Access**: Removed debug mode restrictions from buttons

### ❌ Current Issue: Empty Wizard Form

**Problem**: The "Create Board Resolution" wizard form displays empty when accessed via:
- Menu: Vorstandsbeschlüsse → Create Board Resolution
- Button: In project tasks (when available)

**Last Attempted Fix** (deployed at 23:40):
```xml
<!-- wizards/wizard_views.xml line 9-11 -->
<form string="Create Board Resolution">
    <!-- Step field for debugging - hidden later -->
    <field name="step" invisible="1"/>
```

**Symptoms**:
- Form opens but shows no content
- No JavaScript errors reported by user
- Step field properly declared at beginning of form
- All div sections have proper invisibility conditions

## Investigation Checklist

### 1. Check Step Field Initialization
```python
# wizards/create_resolution_wizard.py line 12-18
step = fields.Selection([
    ('basic', 'Basic Information'),
    ('attendance', 'Attendance'),
    ('resolution', 'Resolution Text'),
    ('voting', 'Voting'),
    ('confirmation', 'Confirmation')
], string='Step', default='basic')  # ← Verify default is set
```

### 2. Debug Visibility Conditions
The form uses `invisible="[('step', '!=', 'basic')]"` conditions. If step field isn't properly initialized, all sections might be hidden.

**Quick Test**: Temporarily make step field visible:
```xml
<field name="step" invisible="0"/>  <!-- Make visible for debugging -->
```

### 3. Check for JavaScript Errors
SSH into server and check browser console:
```bash
ssh kulturhaus
sudo tail -f /var/log/odoo/odoo18.log
# Then open wizard and check for errors
```

### 4. Verify Field Dependencies
Each step div depends on the step field value. Check if the field is being computed correctly.

## Possible Solutions

### Solution 1: Force Initial Step Display
```xml
<!-- Make first step always visible as fallback -->
<div invisible="0" attrs="{'invisible': [('step', 'not in', ['basic', False])]}">
    <h2>Step 1: Basic Information</h2>
    <!-- content -->
</div>
```

### Solution 2: Add Form Sheet Structure
```xml
<form string="Create Board Resolution">
    <sheet>
        <field name="step" invisible="1"/>
        <!-- rest of form content -->
    </sheet>
    <footer>
        <!-- buttons -->
    </footer>
</form>
```

### Solution 3: Check Model Registration
Verify the transient model is properly registered:
```python
# In __init__.py
from . import wizards
# In wizards/__init__.py
from . import create_resolution_wizard
```

## Server Access & Deployment

### Quick Commands
```bash
# SSH access
ssh kulturhaus

# Check service
sudo systemctl status odoo18

# View logs
sudo tail -f /var/log/odoo/odoo18.log

# Deploy module updates
cd /Users/larsweiler/Development/iwg-work/kulturhaus-bortfeld-de
./deploy_board_module.sh

# Restart service
./restart_service.sh
```

### File Locations on Server
```
/opt/odoo18/odoo/addons/kulturhaus_board_resolutions/
├── wizards/
│   ├── wizard_views.xml  # Empty form issue here
│   └── create_resolution_wizard.py
└── __manifest__.py
```

## Next Steps Priority

1. **Immediate**: Fix wizard form display issue
2. **Test**: Verify complete workflow after fix:
   - Create resolution with wizard
   - Check attendance tracking
   - Test voting functionality
   - Verify PDF export
3. **Polish**: German translations if needed
4. **Document**: Update user documentation

## Module Purpose Reminder

This module manages Vorstandsbeschlüsse (board resolutions) for German Verein compliance:
- Auto-numbering: VB-YYYY-NNN format
- Workflow: draft → voted → to_approve → approved → archived
- Quorum validation
- Voting tracking (open/secret)
- PDF export for official records

## Contact & Environment

- **Server**: kulturhaus (193.30.120.108)
- **URL**: https://kulturhaus-bortfeld.de
- **Database**: kulturhive
- **Odoo Version**: 18 Community Edition

## Critical Notes

⚠️ **Security**: Database manager was exposed yesterday - now fixed with:
```conf
list_db = False
dbfilter = ^kulturhive$
```

⚠️ **User Feedback**: User frustrated with repeated Odoo 18 compatibility mistakes - double-check all changes against Odoo 18 documentation

---

**Handover prepared by**: Claude Code
**For next session**: Start by investigating why wizard form displays empty