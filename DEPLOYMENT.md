# Deployment Guide - Kulturhaus Bortfeld Odoo

**Self-hosted Odoo with GitHub Integration**

## 🔄 Deployment Architecture

```
GitHub Repository
       ↓
   Local Development
       ↓
   Production Server
   (kulturhaus-bortfeld.de)
```

## 📁 Repository Structure

```
kulturhaus-bortfeld-de/
├── .gitignore                     # Git ignore patterns
├── CLAUDE.md                      # Project context & quick reference
├── TECHNICAL_DOCUMENTATION.md    # Comprehensive server docs
├── DEPLOYMENT.md                  # This deployment guide
├── README.md                      # Project overview
├── server-info.md                # Basic server information
├── ip-whitelist-config.md         # Security configuration
├── ssh-setup.md                   # SSH configuration history
├── custom-addons/                 # Custom Odoo modules (future)
├── configurations/                # Server config templates
│   ├── nginx/                     # Nginx configurations
│   ├── odoo/                      # Odoo configuration templates
│   └── ssl/                       # SSL setup scripts
├── scripts/                       # Deployment & maintenance scripts
│   ├── backup.sh                  # Database backup script
│   └── health-check.sh            # Server health monitoring
└── docs/                          # Additional documentation
    ├── user-guides/               # End-user documentation
    └── api/                       # API documentation
```

## 🚀 Deployment Workflow

### For Self-hosted Odoo Projects

**Option 1: Documentation & Configuration Management (Recommended)**
```bash
# This repository manages:
# - Server documentation and procedures
# - Configuration files and templates  
# - Custom Odoo modules and addons
# - Deployment scripts and automation
# - Backup and maintenance procedures
```

**Option 2: Full Application Deployment**
```bash
# Advanced: Deploy entire Odoo instance from Git
# - Odoo source code and custom modules
# - Database migration scripts
# - Infrastructure as Code (IaC)
# - Automated testing and deployment
```

## 🔧 Current Setup (Option 1)

### What's in Version Control
✅ **Documentation**: Technical docs, procedures, guides  
✅ **Configuration Templates**: Nginx, Odoo config examples  
✅ **Scripts**: Backup, deployment, monitoring scripts  
✅ **Custom Modules**: Any custom Odoo addons (future)  
✅ **Security Configs**: IP whitelist, SSL setup procedures  

### What's NOT in Version Control
❌ **Sensitive Data**: Passwords, SSH keys, certificates  
❌ **Live Configuration**: Actual server config files with secrets  
❌ **Database Data**: Production database content  
❌ **Log Files**: Server logs and temporary files  

## 📋 Development Workflow

### 1. Local Development
```bash
# Clone repository
git clone https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git
cd kulturhaus-bortfeld-de

# Make changes to documentation, scripts, or custom modules
vim TECHNICAL_DOCUMENTATION.md

# Test scripts locally (if applicable)
./scripts/health-check.sh
```

### 2. Version Control
```bash
# Stage changes
git add .

# Commit with clear message
git commit -m "docs: Update server configuration documentation"

# Push to GitHub
git push origin main
```

### 3. Deployment to Production
```bash
# SSH into production server
ssh kulturhaus

# Clone repository to server (first time only)
cd /opt/
sudo git clone https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git kulturhaus-docs
sudo chown -R khaus:khaus /opt/kulturhaus-docs/

# Or pull latest documentation/scripts (subsequent updates)
cd /opt/kulturhaus-docs/
git pull origin main

# Apply configuration changes (manually)
sudo cp configurations/nginx/kulturhaus-bortfeld.conf.template /etc/nginx/sites-available/kulturhaus-bortfeld.conf
sudo systemctl reload nginx

# Run maintenance scripts
./scripts/backup.sh
./scripts/health-check.sh
```

## 🔄 GitHub Integration Options

### Option A: Documentation Repository (Current)
**What it manages:**
- Server documentation and procedures
- Configuration templates and examples
- Deployment scripts and automation
- Custom Odoo modules (when developed)

**Benefits:**
- Simple to set up
- Great for team collaboration on docs
- Version control for procedures
- Safe (no sensitive data)

### Option B: Full DevOps Pipeline (Advanced)
**What it could manage:**
- Complete Odoo application deployment
- Database migrations
- Infrastructure as Code
- Automated testing and CI/CD

**Implementation:**
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to server
        run: |
          ssh ${{ secrets.SERVER_USER }}@${{ secrets.SERVER_HOST }} \
          "cd /opt/odoo-deployment && git pull && ./deploy.sh"
```

## 🛠️ Setting Up GitHub Repository

### ✅ Step 1: GitHub Repository (COMPLETED)
Repository already created at: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de

### ✅ Step 2: Repository Setup (COMPLETED)
```bash
# Repository is linked and operational
git remote -v
# origin https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git

# Current status
git status
# On branch main, up to date with origin/main
```

### Step 3: Team Access Setup
```bash
# On GitHub.com:
# Go to: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de
# Settings → Manage access → Invite collaborators
# Add team members with appropriate permissions
```

## 🔐 Security Considerations

### Sensitive Data Management
```bash
# NEVER commit to Git:
- SSH private keys
- Database passwords  
- SSL certificates
- Production configuration files with secrets

# DO commit to Git:
- Documentation and procedures
- Configuration templates (without secrets)
- Deployment scripts
- Custom code and modules
```

### Environment Variables
```bash
# Use environment variables for secrets
# Example in deployment script:
export DB_PASSWORD="${ODOO_DB_PASSWORD}"
export ADMIN_PASSWORD="${ODOO_ADMIN_PASSWORD}"
```

## 📊 Monitoring & Maintenance

### Automated Health Checks
```bash
# scripts/health-check.sh
#!/bin/bash
curl -f https://kulturhaus-bortfeld.de > /dev/null
systemctl is-active odoo18 nginx postgresql
df -h | grep -E "9[0-9]%" # Alert if disk >90%
```

### Backup Automation
```bash
# scripts/backup.sh
#!/bin/bash
DATE=$(date +%Y%m%d)
sudo -u postgres pg_dump kulturhive > "/backup/kulturhive_${DATE}.sql"
tar -czf "/backup/odoo_filestore_${DATE}.tar.gz" /opt/odoo18/filestore/
```

## 🎯 Recommended Next Steps

### ✅ Completed Setup
1. ✅ **GitHub repository created** (private) - https://github.com/syntax-sabotage/kulturhaus-bortfeld-de
2. ✅ **Initial commit completed** with comprehensive documentation
3. ✅ **Repository structure established** with scripts and configurations
4. ✅ **Deployment procedures documented** in this guide

### Remaining Setup
1. **Set up team access** for additional collaborators
2. **Clone repository to production server** for script deployment

### Future Enhancements
1. **Custom Odoo modules** development workflow
2. **Automated backup** to cloud storage
3. **CI/CD pipeline** for advanced deployment
4. **Infrastructure monitoring** integration

## 🔗 Useful Resources

### GitHub & Git
- [GitHub Documentation](https://docs.github.com)
- [Git Best Practices](https://git-scm.com/doc)
- [GitHub Actions](https://docs.github.com/en/actions)

### Odoo Development
- [Odoo Developer Documentation](https://www.odoo.com/documentation/18.0/developer/)
- [Custom Addons Development](https://www.odoo.com/documentation/18.0/developer/tutorials/getting_started.html)

### DevOps & Deployment
- [Server Automation Best Practices](https://docs.ansible.com/ansible/latest/user_guide/playbooks_best_practices.html)
- [Database Migration Strategies](https://www.postgresql.org/docs/current/backup.html)

---

*This deployment strategy balances simplicity with professional development practices, perfect for self-hosted Odoo management.*