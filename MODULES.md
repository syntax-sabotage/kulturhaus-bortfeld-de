# Kulturhaus Bortfeld - Installed Odoo Modules

**Last Updated**: 2025-09-17  
**Odoo Version**: 18.2a1 Community Edition  
**Database**: kulturhive  
**Location**: `/opt/odoo18/odoo/addons/`

## 📦 Custom Kulturhaus Modules

### Core Modules
| Module | Description | Status | Version | Notes |
|--------|-------------|--------|---------|-------|
| **kulturhaus_dashboard** | Custom dashboard for operations | ✅ Installed | 1.0.0 | Main operations dashboard |
| **kulturhaus_calendar_subscription** | Calendar subscription features | ✅ Installed | 1.0.0 | Calendar integration |
| **kulturhaus_simplified_checkout** | Simplified checkout process | ✅ Installed | 1.0.0 | Streamlined checkout |
| **kh_menu_organizer** | Menu organization tool | ✅ Installed | 1.0.0 | Menu management |
| **kulturhaus_vereinsarbeit_core** | Vereinsarbeit & Mitgliederverwaltung | ✅ Installed | 18.2.1.0.0 | Club management system |

### Notification Modules
| Module | Description | Status | Version | Notes |
|--------|-------------|--------|---------|-------|
| **kulturhaus_push** | Push notifications system | ✅ Installed | 1.0.0 | Main notification module |
| **push_simple** | Base push notification support | ✅ Installed | 1.0.0 | Base module for push |
| **sttl_channel_notification** | Channel notification system | ✅ Installed | 1.0.0 | Channel notifications |

## 🌍 OCA (Odoo Community Association) Modules

### Project Enhancement Modules (Added 2025-09-17)
| Module | Description | Status | Version | Use Case |
|--------|-------------|--------|---------|----------|
| **project_role** | Project roles management | ✅ Installed | 18.2.1.0.0 | Assign roles like Vorstand, AG-Leiter |
| **project_template** | Project templates | ✅ Installed | 18.2.1.0.0 | Event templates - **Modified*** |
| **project_task_default_stage** | Default task stages | ✅ Installed | 18.2.1.0.0 | Workflow automation |
| **project_tag_hierarchy** | Hierarchical project tags | ✅ Installed | 18.2.1.0.0 | Organize events hierarchically |
| **project_parent_task_filter** | Parent task filtering | ✅ Installed | 18.2.1.0.0 | Task hierarchy management |
| **project_task_add_very_high** | Very high priority for tasks | ✅ Installed | 18.2.1.0.0 | Critical task prioritization |
| **project_key** | Project short codes | ✅ Installed | 18.2.1.0.0 | Quick project references (EK2025) |

***Important Note**: The `project_template` module was modified on 2025-09-17 to move the "Use as Template" checkbox from the form header to the Settings tab. This fixed a UI overlap issue with the task statistics button.

## 🗑️ Removed/Cleaned Modules

### Removed on 2025-09-17
- `pwa_kulturhaus` - Obsolete PWA module
- `pwa_kulturhaus.backup.20250912` - Backup module  
- `pwa_kulturhaus_backup` - Backup module
- `ce_push_notifications` - Replaced by kulturhaus_push
- `ce_communication_enhancements` - Replaced by newer notification modules

## 📊 Module Statistics

- **Total Custom Modules**: 8
- **Total OCA Modules**: 7  
- **Total Active Modules**: 15
- **Removed Modules**: 5

## 🔧 Module Management Commands

### Check Module Status
```bash
ssh kulturhaus "echo 'Basf1\$Khaus' | sudo -S -u odoo18 psql -d kulturhive -c \"SELECT name, state FROM ir_module_module WHERE state='installed' ORDER BY name;\""
```

### Update Apps List
1. Go to Apps menu in Odoo
2. Click "Update Apps List"
3. Search for specific module
4. Install/Upgrade as needed

### Clear Module Cache
```bash
ssh kulturhaus "echo 'Basf1\$Khaus' | sudo -S rm -rf /opt/odoo18/odoo/.local/share/Odoo/filestore/kulturhive/assets/*"
ssh kulturhaus "echo 'Basf1\$Khaus' | sudo -S systemctl restart odoo18"
```

## 📝 Module Development Notes

### Version Compatibility
All modules have been updated to version 18.2.1.0.0 to match the Odoo 18.2a1 server version. This is critical for proper installation.

### Project Template UI Fix
The `project_template` module's view file (`/opt/odoo18/odoo/addons/project_template/views/project.xml`) was modified directly on the server:
- **Problem**: "Use as Template" checkbox overlapped with task statistics
- **Solution**: Moved checkbox to Settings tab in its own "Template Settings" group
- **File Modified**: `/opt/odoo18/odoo/addons/project_template/views/project.xml`

### Notification System Architecture
```
kulturhaus_push (Main Module)
    └── push_simple (Base Module)
        └── sttl_channel_notification (Channel Support)
```

## 🚀 Next Steps

1. **Configure Project Roles** - Set up roles for Vorstand members
2. **Create Project Templates** - Build templates for recurring events (Konzerte, Theater)
3. **Set Up Task Workflows** - Configure default stages for automated workflows
4. **Implement Project Keys** - Create standardized project codes (KH-2025-xxx)
5. **Test All OCA Modules** - Verify all features work in production

## 🔍 Quick Troubleshooting

### Module Not Installing
1. Check version compatibility (must be 18.2.1.0.0)
2. Clear cache and restart Odoo
3. Check dependencies are installed

### UI Overlap Issues
- Template checkbox is now in Settings tab
- Task button properly positioned in button box

### Missing Modules in Apps List
```bash
# Update module list
ssh kulturhaus "echo 'Basf1\$Khaus' | sudo -S systemctl restart odoo18"
# Then: Apps > Update Apps List
```

---

*Documentation maintained by Claude Code*  
*For server details see CLAUDE.md and TECHNICAL_DOCUMENTATION.md*