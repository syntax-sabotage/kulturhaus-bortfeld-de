# Kulturhaus Bortfeld - Custom Odoo Modules

**Last Updated**: 2025-09-13  
**Odoo Version**: 18.0 Community Edition  
**Location**: `/opt/odoo18/odoo/addons/`  
**Repository**: Module source code now in `/modules/` directory

## 📦 Installed Modules

### Custom Kulturhaus Modules

#### 1. kulturhaus_dashboard
- **Purpose**: Custom dashboard for Kulturhaus operations
- **Status**: ✅ Installed and operational
- **Features**: Customized views and metrics for cultural center management
- **Dependencies**: Standard Odoo modules

#### 2. kulturhaus_calendar_subscription
- **Purpose**: Calendar subscription and synchronization features
- **Status**: ✅ Installed and operational
- **Features**: Allow users to subscribe to event calendars
- **Dependencies**: Standard calendar modules

#### 3. kulturhaus_simplified_checkout
- **Purpose**: Simplified checkout process
- **Status**: ✅ Installed and operational
- **Features**: Streamlined checkout for events and bookings
- **Dependencies**: Website, sale modules

#### 4. kh_menu_organizer
- **Purpose**: Menu organization and management tool
- **Status**: ✅ Installed and operational
- **Features**: Reorganize and customize Odoo menus
- **Dependencies**: Base modules

#### 5. kulturhaus_membership_sepa
- **Purpose**: SEPA direct debit management for memberships
- **Status**: ✅ Installed and operational
- **Features**:
  - SEPA mandate management for members
  - Configurable membership periods (full year/half year)
  - Manual batch generation with buttons
  - SEPA XML export for bank processing
- **Dependencies**: `base`, `membership`, `account`, `contacts`

#### 6. ce_communication_enhancements
- **Purpose**: PWA support and mobile push notifications
- **Status**: ✅ Deployed (2025-09-11)
- **Features**:
  - Progressive Web App (PWA) manifest
  - Service Worker for offline functionality
  - Push notification support for iOS 16.4+
  - Mobile app connectivity enhancements
- **Dependencies**: 
  - Python: `pywebpush`, `cryptography`
  - Odoo: `base`, `web`, `mail`
- **Special Notes**: 
  - Requires HTTPS (already configured)
  - iOS notifications require PWA installation to home screen
  - Includes German setup guide for users

#### 7. kulturhaus_vereinsarbeit_core
- **Purpose**: Kernmodul für Vereinsarbeit und Mitgliederverwaltung
- **Status**: 🚧 In Entwicklung (2025-09-17)
- **Features**: 
  - Mitgliederverwaltung
  - Veranstaltungsplanung
  - Ressourcenverwaltung
  - Aufgabenverwaltung
  - Dokumentenverwaltung
- **Dependencies**: base, mail, contacts, calendar, project

### OCA Project Enhancement Modules (2025-09-17)

#### 1. project_role
- **Purpose**: Rollenverwaltung für Projekte und Teams
- **Status**: ✅ Installed
- **Version**: 18.2.1.0.0 (angepasst für Odoo 18.2)
- **Features**: 
  - Vereinsrollen (Vorstand, Kassenwart, AG-Leiter)
  - Projektbezogene Rollen
  - Rollenbasierte Berechtigungen
- **Source**: OCA/project

#### 2. project_template  
- **Purpose**: Vorlagen für wiederkehrende Projekte/Events
- **Status**: ✅ Installed
- **Version**: 18.2.1.0.0
- **Features**:
  - Event-Vorlagen (Konzert, Theater, Workshop)
  - Checklisten-Vorlagen
  - Aufgabenvorlagen mit Standardzeiten
- **Source**: OCA/project

#### 3. project_task_default_stage
- **Purpose**: Standard-Stages für Aufgaben
- **Status**: ✅ Installed
- **Version**: 18.2.1.0.0
- **Features**: 
  - Automatische Aufgaben-Stages
  - Workflow-Automatisierung
- **Source**: OCA/project

#### 4. project_tag_hierarchy
- **Purpose**: Hierarchische Tags für bessere Organisation
- **Status**: ✅ Installed
- **Version**: 18.2.1.0.0
- **Features**:
  - Verschachtelte Tags (Event→Konzert→Klassik)
  - Bessere Event-Kategorisierung
- **Source**: OCA/project

#### 5. project_parent_task_filter
- **Purpose**: Haupt- und Unteraufgaben-Verwaltung
- **Status**: ✅ Installed  
- **Version**: 18.2.1.0.0
- **Features**:
  - Strukturierung komplexer Events
  - Aufgaben-Hierarchien
- **Source**: OCA/project

#### 6. project_task_add_very_high
- **Purpose**: Kritische Prioritätsstufe für Aufgaben
- **Status**: ✅ Installed
- **Version**: 18.2.1.0.0
- **Features**:
  - Kritische Priorität für Deadline-Tasks
  - Pflichtaufgaben markieren (z.B. GEMA-Meldung)
- **Source**: OCA/project

#### 7. project_key
- **Purpose**: Kurzcodes für Projekte
- **Status**: ✅ Installed
- **Version**: 18.2.1.0.0
- **Features**:
  - Projekt-Kurzcodes (KH-2025-001)
  - Bessere Referenzierung
- **Source**: OCA/project

## 🔧 Module Management

### Installation Commands
```bash
# Restart Odoo to detect new modules
sudo systemctl restart odoo18

# Update module list (from Odoo UI)
Apps > Update Apps List

# Install module (from Odoo UI)
Apps > Search > Install
```

### Module Locations
```bash
# All modules location
/opt/odoo18/odoo/addons/

# List custom modules
ls /opt/odoo18/odoo/addons/ | grep -E '^(kulturhaus|kh_|ce_)'

# Check module status
grep "kulturhaus\|kh_\|ce_" /var/log/odoo/odoo18.log
```

### Backup Modules
```bash
# Backup individual module
tar -czf module_name_backup.tar.gz /opt/odoo18/odoo/addons/module_name/

# Backup all custom modules
for module in kulturhaus_* kh_* ce_*; do
    tar -czf "${module}_backup_$(date +%Y%m%d).tar.gz" "/opt/odoo18/odoo/addons/$module/"
done
```

## 📝 Development Notes

### Adding New Modules
1. Upload module to `/opt/odoo18/odoo/addons/`
2. Set proper permissions: `chown -R odoo18:odoo18 module_name/`
3. Install dependencies if needed: `./venv/bin/pip install package_name`
4. Restart Odoo: `sudo systemctl restart odoo18`
5. Update Apps List in Odoo UI
6. Install module from Apps menu

### Module Dependencies
- All Python dependencies must be installed in Odoo's virtual environment
- Path: `/opt/odoo18/odoo/venv/bin/pip`
- Current special dependencies:
  - `pywebpush` (for ce_communication_enhancements)
  - `cryptography` (already installed)

## 🚀 PWA Setup (ce_communication_enhancements)

### For End Users
1. Open https://kulturhaus-bortfeld.de in Safari (iOS) or Chrome (Android)
2. Add to Home Screen
3. Open from home screen icon
4. Enable notifications when prompted

### For Administrators
1. Generate VAPID keys (one-time setup)
2. Configure in System Parameters
3. Test notifications from user preferences

### Key URLs
- Manifest: https://kulturhaus-bortfeld.de/manifest.json
- Service Worker: https://kulturhaus-bortfeld.de/service-worker.js

## 📊 Module Statistics
- **Total Odoo Modules**: 670+
- **Custom Kulturhaus Modules**: 7
- **OCA Enhancement Modules**: 7
- **Latest Additions**: OCA Project Modules (2025-09-17)
- **Python Virtual Env**: `/opt/odoo18/odoo/venv/`

---

*For detailed server information, see server-info.md*  
*For technical documentation, see TECHNICAL_DOCUMENTATION.md*