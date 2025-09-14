# CLAUDE.md - Kulturhaus Development Environment

**Project**: Kulturhaus Bortfeld e.V. - Odoo Module Development  
**Environment**: Docker Local Development  
**Branch**: develop  
**Production**: https://kulturhaus-bortfeld.de (main branch)

## 🎯 Current Focus
Developing and enhancing Odoo 18 modules for Kulturhaus Bortfeld, especially:
- **kulturhaus_membership_sepa**: SEPA direct debit for memberships
- **kulturhaus_dashboard**: Custom operational dashboards
- **mitmach_portal**: Volunteer management system

## 📁 Project Structure
```
/Users/larsweiler/Development/docker-environments/kulturhaus-dev/
├── addons/                          # Odoo modules (mounted in Docker)
│   ├── kulturhaus_membership_sepa/  # SEPA membership management
│   ├── kulturhaus_dashboard/        # Custom dashboards
│   ├── kulturhaus_calendar_subscription/  # iCal feeds
│   ├── kulturhaus_simplified_checkout/    # Event checkout
│   ├── kh_menu_organizer/          # Menu customization
│   └── mitmach_portal/              # Volunteer management
├── docker-compose.yml               # Docker configuration
├── WORKFLOW_QUICKSTART.md          # Quick reference guide
└── GIT_WORKFLOW.md                 # Detailed Git workflow

GitHub: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de
```

## 🚀 Quick Commands

### Start Development
```bash
cd /Users/larsweiler/Development/docker-environments/kulturhaus-dev
docker-compose up -d
open http://localhost:8070  # admin/admin
```

### Current Task Pattern
1. Always work on `develop` branch or feature branches
2. Test in Docker before committing
3. Create PR to main for production deployment
4. Deploy to VPS after merge

### Module Development
```bash
# Edit modules directly in
addons/kulturhaus_membership_sepa/

# Docker auto-reloads with --dev=all
# Or manually restart:
docker-compose restart kulturhaus-odoo
```

## 🔄 Git Workflow

### Daily Workflow
```bash
git checkout develop
git pull origin develop
# Make changes
git add .
git commit -m "feat: Description"
git push origin develop
```

### Feature Development
```bash
git checkout -b feature/new-feature
# Develop and test
git push origin feature/new-feature
# Create PR on GitHub
```

## 🌐 Environments

### Local Docker (Development)
- URL: http://localhost:8070
- DB: kulturhaus_dev
- Login: admin/admin
- Branch: develop

### VPS Production
- URL: https://kulturhaus-bortfeld.de
- Server: 193.30.120.108
- User: khaus (SSH-Key: ~/.ssh/kulturhaus_vps)
- Branch: main
- DB: kulturhive

## 📦 Active Modules

### kulturhaus_membership_sepa
- SEPA mandate management
- Batch generation for direct debits
- XML export for banks
- **Status**: Needs enhancements

### kulturhaus_dashboard
- Configurable dashboard cards
- Statistics and KPIs
- **Status**: Operational

### mitmach_portal
- Volunteer management
- Shift planning
- QR check-in/out
- Telegram bot integration
- **Status**: Fully developed

## 🎯 Current Tasks
- Enhance SEPA membership module
- Add automatic batch generation
- Improve member communication features
- Integrate with existing systems

## 🔧 Development Tips

### Module Installation
1. Apps → Update Apps List
2. Search "kulturhaus"
3. Install/Upgrade

### Debugging
```bash
docker logs -f kulturhaus-odoo
docker exec -it kulturhaus-odoo bash
```

### Database Access
```bash
docker exec -it kulturhaus-db psql -U odoo18 -d kulturhaus_dev
```

### ⚠️ Odoo 17+ Breaking Changes
**WICHTIG für Odoo 17/18 Kompatibilität:**

1. **View Type Change (Odoo 18)**: `tree` → `list`
   ```xml
   <!-- FALSCH (Odoo < 18) -->
   <tree string="My View">
   
   <!-- RICHTIG (Odoo 18) -->
   <list string="My View">
   ```
   
2. **Attrs Deprecated (Odoo 17+)**: `attrs` → direkte Attribute
   ```xml
   <!-- FALSCH (Odoo < 17) -->
   <field name="field" attrs="{'invisible': [('state', '=', 'done')]}"/>
   
   <!-- RICHTIG (Odoo 17+) -->
   <field name="field" invisible="state == 'done'"/>
   ```
   
3. **Chatter benötigt mail.thread**:
   ```python
   class MyModel(models.Model):
       _inherit = ['mail.thread', 'mail.activity.mixin']
   ```
   Dependency: `'depends': [..., 'mail']`

## 📝 Important Notes
- NEVER commit directly to main
- ALWAYS test in Docker first
- Use German for all UI elements
- Follow Odoo 18 best practices
- Document all module changes

## 🌐 Domain Structure
**WICHTIG - Domain Konvention:**
- **Öffentlich**: `kulturhaus-bortfeld.de` (MIT Bindestrich)
  - Hauptwebsite, Odoo ERP
- **Intern**: `kulturhausbortfeld.de` (OHNE Bindestrich)
  - Nextcloud, Vaultwarden, interne Services
  - sec.kulturhausbortfeld.de (Passwortmanager)

## 🚨 Emergency Contacts
- VPS Issues: Check LuckySrv status
- GitHub: @syntax-sabotage
- Production DB: kulturhive (not erp!)
- Vaultwarden Admin Token: Check ~/vaultwarden/.env on VPS
- System-Benachrichtigungen: it@kulturhaus-bortfeld.de

## 🤖 Telegram Bot Development

### Bot Details
- **Bot Name**: @taktgeber_bot
- **Token**: 8232267547:AAEZJ8sl4WhjY2jz61SZCpotCHsLhjsF1zM
- **Channel**: https://t.me/+U_DXMrXdz8BjN2Ni
- **Admin Chat ID**: 160606654

### Connect VPS Bot to Local Development
```bash
# 1. Start local Docker environment
cd /Users/larsweiler/Development/docker-environments/kulturhaus-dev
docker-compose up -d

# 2. Create SSH reverse tunnel (local port 8070 → VPS port 9069)
sshpass -p 'Basf1$Khaus' ssh -R 9069:localhost:8070 -N -f khaus@193.30.120.108

# 3. Bot will connect to local Odoo via localhost:9069
# Test with: /status, /registrieren, /punkte commands
```

### Bot Files on VPS
- **Location**: `/home/khaus/mitmach_bot/`
- **Config**: `/home/khaus/mitmach_bot/.env`
- **Start/Stop**: `/home/khaus/mitmach_bot/start_bot.sh {start|stop|restart|status}`
- **Logs**: `/home/khaus/mitmach_bot/bot.log`

### Switch Between Environments
```bash
# For Development (local Docker)
ODOO_URL=http://localhost:9069
ODOO_DB=kulturhaus_dev
ODOO_USERNAME=admin
ODOO_PASSWORD=admin

# For Production
ODOO_URL=http://localhost:8069
ODOO_DB=kulturhive
ODOO_USERNAME=admin
ODOO_PASSWORD=Khausb2024
```

### Kill SSH Tunnel
```bash
ps aux | grep "ssh -R 9069" | awk '{print $2}' | xargs kill
```

## 🎬 Session Context
Working on Kulturhaus module development with focus on membership management and SEPA integration. Docker environment configured, Git workflow established with develop/main branches. Telegram bot configured to connect to local development environment via SSH tunnel.

---
**Quick Help**: See WORKFLOW_QUICKSTART.md for commands