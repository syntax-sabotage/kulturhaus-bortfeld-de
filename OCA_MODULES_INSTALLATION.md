# OCA Modules Installation Log

**Date**: 2025-09-17  
**Installed By**: Claude Code  
**Server**: kulturhaus-bortfeld.de (193.30.120.108)  
**Odoo Version**: 18.2a1  

## Installation Summary

Successfully installed 7 OCA Project Enhancement modules from the OCA/project repository to enhance the Kulturhaus Vereinsarbeit capabilities.

## Modules Installed

### 1. project_role
- **Version**: 18.2.1.0.0 (adapted from 18.0.1.0.0)
- **Purpose**: Project role-based roster and permissions
- **Use Case**: Managing Vereinsrollen (Vorstand, Kassenwart, AG-Leiter)

### 2. project_template
- **Version**: 18.2.1.0.0
- **Purpose**: Project templates for recurring events
- **Use Case**: Event templates (Konzert, Theater, Workshop, Mitgliederversammlung)

### 3. project_task_default_stage
- **Version**: 18.2.1.0.0
- **Purpose**: Default stages for project tasks
- **Use Case**: Workflow automation (Idee → Planung → Durchführung → Nachbereitung)

### 4. project_tag_hierarchy  
- **Version**: 18.2.1.0.0
- **Purpose**: Hierarchical tag system
- **Use Case**: Nested categorization (Event→Konzert→Klassik)

### 5. project_parent_task_filter
- **Version**: 18.2.1.0.0
- **Purpose**: Parent/child task relationships
- **Use Case**: Complex event structuring with subtasks

### 6. project_task_add_very_high
- **Version**: 18.2.1.0.0
- **Purpose**: Additional "Very High" priority level
- **Use Case**: Critical tasks (GEMA-Meldung, Versicherung)

### 7. project_key
- **Version**: 18.2.1.0.0
- **Purpose**: Short reference keys for projects
- **Use Case**: Project codes (KH-2025-001)

## Technical Details

### Version Compatibility Fix

The OCA modules were originally designed for Odoo 18.0 but needed adaptation for Odoo 18.2:

```bash
# Original version in manifests
"version": "18.0.1.0.0"

# Updated to
"version": "18.2.1.0.0"
```

### Installation Process

1. **Module Upload**: Transferred via SCP to `/opt/odoo18/odoo/addons/`
2. **Permission Fix**: Set ownership to `odoo18:odoo18`
3. **Version Adaptation**: Modified `__manifest__.py` files for version compatibility
4. **Service Restart**: Restarted Odoo service
5. **Module Activation**: Installed via Odoo Apps interface

### File Locations

```bash
/opt/odoo18/odoo/addons/project_role/
/opt/odoo18/odoo/addons/project_template/
/opt/odoo18/odoo/addons/project_task_default_stage/
/opt/odoo18/odoo/addons/project_tag_hierarchy/
/opt/odoo18/odoo/addons/project_parent_task_filter/
/opt/odoo18/odoo/addons/project_task_add_very_high/
/opt/odoo18/odoo/addons/project_key/
```

## Configuration Recommendations

### Next Steps

1. **Configure Roles** (project_role):
   - Vorstandsmitglied
   - Kassenwart
   - AG-Leiter
   - Veranstaltungsleiter
   - Helfer

2. **Create Templates** (project_template):
   - Konzert-Template
   - Theater-Template  
   - Workshop-Template
   - Mitgliederversammlung-Template

3. **Define Stages** (project_task_default_stage):
   - Idee
   - Planung
   - Genehmigung
   - Vorbereitung
   - Durchführung
   - Nachbereitung

4. **Setup Tag Hierarchy** (project_tag_hierarchy):
   ```
   Veranstaltung
   ├── Konzert
   │   ├── Klassik
   │   ├── Jazz
   │   └── Rock
   ├── Theater
   │   ├── Schauspiel
   │   └── Musical
   └── Workshop
       ├── Musik
       └── Kunst
   ```

5. **Configure Project Keys** (project_key):
   - Format: KH-YYYY-NNN
   - Example: KH-2025-001

## Troubleshooting Log

### Issue 1: Version Incompatibility
- **Problem**: Modules marked as "nicht installierbar" due to version mismatch
- **Solution**: Updated manifest versions from 18.0.1.0.0 to 18.2.1.0.0
- **Script Used**: `/tmp/fix_modules.sh`

### Issue 2: Permission Issues
- **Problem**: Wrong ownership (odoo:odoo instead of odoo18:odoo18)
- **Solution**: Fixed with `chown -R odoo18:odoo18`

## Backup Information

Original module archives stored at:
- Local: `/tmp/kulturhaus_oca_modules.tar.gz`
- Server: `/tmp/kulturhaus_oca_modules.tar.gz`

## Resources

- **OCA Repository**: https://github.com/OCA/project
- **Module Documentation**: https://github.com/OCA/project/tree/18.0
- **Odoo 18 Docs**: https://www.odoo.com/documentation/18.0/

## Status

✅ **All modules successfully installed and operational**

---

*Installation completed: 2025-09-17 12:18 CET*  
*Performed by: Claude Code*  
*Verified by: User confirmation*