# Kulturhaus Bortfeld e.V. - Odoo ERP Server

**Status**: ✅ **PRODUCTION OPERATIONAL**  
**Live Website**: https://kulturhaus-bortfeld.de  
**Last Updated**: 2025-06-12  

## 🏢 Project Overview
- **Customer**: Kulturhaus Bortfeld e.V.
- **Type**: Odoo 18 ERP (Self-hosted on Ubuntu VPS)
- **Domain**: kulturhaus-bortfeld.de
- **Server**: v2202411240735294743.luckysrv.de (193.30.120.108)
- **Hosting**: LuckySrv VPS (not Odoo.sh, not Docker)
- **Status**: ✅ Production Ready & Operational

## 📋 Description
Self-hosted Odoo 18 ERP system for Kulturhaus Bortfeld e.V. - a cultural center managing events, memberships, and operations. Deployed directly on Ubuntu 24.04 LTS with native installation for optimal performance and control.

## 🏗️ Technical Architecture
- **Deployment**: Native Ubuntu installation (not containerized)
- **OS**: Ubuntu 24.04.1 LTS
- **Database**: PostgreSQL 16
- **Web Server**: Nginx reverse proxy with SSL
- **SSL**: Let's Encrypt with auto-renewal
- **Security**: fail2ban, UFW firewall, SSH keys
- **Performance**: Multi-worker Odoo setup (8 workers)

## 📁 Repository Structure
```
kulturhaus-bortfeld-de/
├── README.md                           # This overview
├── CLAUDE.md                          # Project context & quick reference  
├── TECHNICAL_DOCUMENTATION.md        # Complete technical documentation
├── DEPLOYMENT.md                     # GitHub workflow & deployment guide
├── server-info.md                    # Server specifications & status
├── ssh-setup.md                      # SSH configuration (completed)
├── ip-whitelist-config.md           # Security configuration
├── .gitignore                       # Git ignore patterns
├── scripts/                         # Automation scripts
│   ├── health-check.sh             # System health monitoring
│   └── backup.sh                   # Database & file backup
├── configurations/                  # Configuration templates
│   ├── nginx/                      # Nginx configuration templates
│   └── odoo/                       # Odoo configuration examples
└── docs/                           # Additional documentation
    └── user-guides/                # End-user documentation (future)
```

## 🚀 Current Status

### ✅ Fully Operational Services
- **Odoo 18 ERP**: Multi-worker production setup
- **PostgreSQL 16**: Database with kulturhive schema
- **Nginx**: Reverse proxy with SSL termination
- **Let's Encrypt SSL**: Auto-renewal configured
- **Security**: fail2ban, firewall, SSH hardening
- **Monitoring**: Health checks and logging

### 📊 Performance Metrics
- **Response Time**: <1 second
- **Memory Usage**: 2.8GB/8GB (65% available)
- **Disk Usage**: 8.4GB/251GB (97% available)  
- **Uptime**: Stable production environment

## 🔧 Quick Start

### Access the System
```bash
# Production website
https://kulturhaus-bortfeld.de

# SSH into server
ssh kulturhaus

# Run health check
./scripts/health-check.sh

# Create backup
./scripts/backup.sh
```

### For Developers
```bash
# Clone repository
git clone https://github.com/syntax-sabotage/kulturhaus-bortfeld-de.git

# Review technical documentation
cat TECHNICAL_DOCUMENTATION.md

# Check server status
ssh kulturhaus "systemctl status odoo18 nginx postgresql"
```

## 📚 Documentation

### Essential Reading
1. **[CLAUDE.md](CLAUDE.md)** - Project context and quick reference
2. **[TECHNICAL_DOCUMENTATION.md](TECHNICAL_DOCUMENTATION.md)** - Complete technical specs
3. **[DEPLOYMENT.md](DEPLOYMENT.md)** - GitHub workflow and deployment
4. **[server-info.md](server-info.md)** - Current server status

### Quick References
- **SSH Access**: `ssh kulturhaus` (key + password auth)
- **Admin User**: khaus 
- **Database**: kulturhive (PostgreSQL 16)
- **Logs**: `/var/log/odoo/odoo18.log`

## 🔐 Security Features
- ✅ **SSL/TLS**: A+ grade encryption with Let's Encrypt
- ✅ **Firewall**: UFW configured with service rules
- ✅ **SSH**: ed25519 key authentication + fail2ban
- ✅ **IP Whitelist**: Permanent whitelist for admin IP
- ✅ **Security Headers**: Nginx security headers active
- ✅ **Database**: Local access only (no external exposure)

## 🔄 Maintenance

### Automated
- **SSL Renewal**: Let's Encrypt auto-renewal
- **Log Rotation**: System-managed log rotation
- **Service Monitoring**: systemd service management

### Manual (Recommended)
- **Daily**: Health checks via `./scripts/health-check.sh`
- **Weekly**: Backups via `./scripts/backup.sh`
- **Monthly**: System updates and security patches

## 📞 Support

### Technical Access
- **SSH**: `ssh kulturhaus` 
- **GitHub**: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de
- **Server Provider**: LuckySrv

### Emergency Procedures
1. Check service status: `systemctl status odoo18 nginx postgresql`
2. Review logs: `tail -f /var/log/odoo/odoo18.log`
3. Run health check: `./scripts/health-check.sh`
4. Contact hosting provider if server unreachable

## 🎯 Project Success

**🎉 DEPLOYMENT COMPLETE**

The Kulturhaus Bortfeld e.V. server is fully operational with:
- ✅ Production-ready Odoo 18 ERP system
- ✅ Professional security and performance configuration  
- ✅ Complete documentation and development workflow
- ✅ GitHub integration for team collaboration
- ✅ Automated monitoring and backup capabilities

**Ready for business operations at https://kulturhaus-bortfeld.de** 🚀

---

*Deployed with native Ubuntu installation for optimal performance and reliability.*