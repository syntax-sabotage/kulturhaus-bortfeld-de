# Server Information

**Status**: ✅ PRODUCTION OPERATIONAL  
**Last Updated**: 2025-09-11  
**Environment**: Production  

## VPS Details
- **Hostname**: v2202411240735294743.luckysrv.de
- **IP Address**: 193.30.120.108
- **Provider**: LuckySrv
- **Purpose**: Odoo ERP hosting for Kulturhaus Bortfeld e.V.
- **Location**: Germany (datacenter TBD)

## Access Information
- **Domain**: ✅ kulturhaus-bortfeld.de (LIVE)
- **Website**: https://kulturhaus-bortfeld.de
- **SSH User**: khaus
- **SSH Password**: [REMOVED-USE-SSH-KEY]
- **SSH Key**: ed25519 (kulturhaus_bortfeld)
- **Admin Panel**: Odoo Web Interface

## Server Configuration
- **OS**: Ubuntu 24.04.1 LTS (Noble)
- **RAM**: 8GB (5GB available)
- **Storage**: 251GB SSD (233GB available)
- **CPU**: Multi-core VPS
- **Architecture**: x86_64

## ✅ Deployed Services (OPERATIONAL)
- **Odoo 18 Community Edition**: ✅ Running (8 workers + 1 gevent, port 8069)
- **PostgreSQL 16**: ✅ Running (database: kulturhive)
- **Nginx**: ✅ Running (reverse proxy, SSL termination)
- **Let's Encrypt SSL**: ✅ Active (auto-renewal configured)
- **Fail2ban**: ✅ Active (IP: 94.31.75.76 whitelisted)
- **SSH**: ✅ Active (key + password authentication)

## 📦 Custom Odoo Modules (INSTALLED)
- **kulturhaus_dashboard**: Custom dashboard for Kulturhaus operations
- **kulturhaus_calendar_subscription**: Calendar subscription features
- **kulturhaus_simplified_checkout**: Simplified checkout process
- **kh_menu_organizer**: Menu organization tool
- **ce_communication_enhancements**: PWA notifications & mobile connectivity (NEW)

## ✅ Security Configuration (IMPLEMENTED)
- **Firewall**: UFW configured and active
- **SSH Authentication**: Key-based (ed25519) + password backup
- **SSL/TLS**: Let's Encrypt with auto-renewal
- **IP Whitelisting**: fail2ban configured
- **Security Headers**: Nginx security headers active
- **Database Security**: Local access only (localhost:5432)

## Performance Metrics
- **Response Time**: <1 second (typical pages)
- **Memory Usage**: 2.8GB/8GB used (65% available)
- **Disk Usage**: 8.4GB/251GB used (97% available)
- **Database Connections**: ~20 active connections
- **SSL Grade**: A+ (expected with current config)

## ✅ Monitoring (ACTIVE)
- **Health Check Script**: `/scripts/health-check.sh`
- **Backup System**: `/scripts/backup.sh` (manual/scheduled)
- **Log Monitoring**: 
  - Odoo: `/var/log/odoo/odoo18.log`
  - Nginx: `/var/log/nginx/kulturhaus-*.log`
  - System: `/var/log/syslog`

## Network Configuration
- **HTTP**: Port 80 → HTTPS redirect
- **HTTPS**: Port 443 (SSL termination)
- **SSH**: Port 22 (secured)
- **Odoo**: Port 8069 (localhost only)
- **PostgreSQL**: Port 5432 (localhost only)
- **WebSocket**: Port 8072 (Odoo chat/real-time)

## Backup Strategy
- **Database**: PostgreSQL dumps (kulturhive)
- **Filestore**: Odoo attachment files
- **Configuration**: System config files
- **SSL Certificates**: Let's Encrypt certificates
- **Retention**: 7 daily, 4 weekly (recommended)

## Contact Information
- **Technical Admin**: khaus (SSH access)
- **Hosting Provider**: LuckySrv
- **Domain Registrar**: TBD
- **SSL Provider**: Let's Encrypt (free)
- **GitHub Repository**: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de

## Quick Access Commands
```bash
# SSH into server
ssh kulturhaus

# Check all services
ssh kulturhaus "systemctl status odoo18 nginx postgresql"

# Health check
./scripts/health-check.sh

# Backup
./scripts/backup.sh
```

## Service URLs
- **Production Website**: https://kulturhaus-bortfeld.de
- **Odoo Admin Login**: https://kulturhaus-bortfeld.de/web/login
- **Server Direct**: http://193.30.120.108 (redirects to HTTPS)

---

*Server fully operational and ready for business use. All services monitored and documented.*