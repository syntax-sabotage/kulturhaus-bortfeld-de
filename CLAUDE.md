# CLAUDE.md - Kulturhaus Bortfeld e.V. Project Context

**Version**: 1.0  
**Date**: 2025-06-12  
**Project**: Kulturhaus Bortfeld e.V. - Odoo ERP System  
**Status**: ✅ PRODUCTION OPERATIONAL  

---

## 🏢 Project Overview

**Organization**: Kulturhaus Bortfeld e.V.  
**Purpose**: Cultural center management via Odoo ERP system  
**Website**: https://kulturhaus-bortfeld.de  
**Environment**: Production server (fully operational)  

---

## 🖥️ Server Infrastructure

### Production Server Details
- **Provider**: LuckySrv
- **Hostname**: v2202411240735294743.luckysrv.de
- **IP Address**: 193.30.120.108
- **Domain**: kulturhaus-bortfeld.de
- **OS**: Ubuntu 24.04.1 LTS
- **Resources**: 8GB RAM, 251GB SSD storage

### SSH Access Configuration
```bash
# Quick SSH access
ssh kulturhaus

# SSH configuration (already in ~/.ssh/config)
Host kulturhaus
    HostName v2202411240735294743.luckysrv.de
    User khaus
    IdentityFile ~/.ssh/kulturhaus_bortfeld
    IdentitiesOnly yes
```

**SSH Credentials:**
- User: `khaus`
- Password: `Basf1$Khaus`
- SSH Key: `~/.ssh/kulturhaus_bortfeld` (ed25519)

---

## 🚀 Application Stack

### Odoo 18 ERP System
- **Status**: ✅ PRODUCTION RUNNING
- **URL**: https://kulturhaus-bortfeld.de
- **Version**: Odoo 18 (latest stable)
- **Database**: PostgreSQL 16 (database: kulturhive)
- **Configuration**: Multi-worker setup (8 workers)
- **Admin Password**: `khaus`

### Core Services Status
| Service | Status | Port | Purpose |
|---------|--------|------|---------|
| **Odoo 18** | ✅ Running | 8069 | ERP Application |
| **PostgreSQL 16** | ✅ Running | 5432 | Database |
| **Nginx** | ✅ Running | 80/443 | Web Server/SSL |
| **SSH** | ✅ Running | 22 | Remote Access |

---

## 🔐 Security & Access

### Security Features
- ✅ **SSL/TLS**: Let's Encrypt certificates (auto-renewal)
- ✅ **Fail2ban**: IP whitelisting configured (94.31.75.76)
- ✅ **SSH Keys**: ed25519 key authentication
- ✅ **Firewall**: UFW configured
- ✅ **Proxy Mode**: Nginx reverse proxy with security headers

### Access Control
- **SSH Access**: Key-based authentication (password backup)
- **Odoo Admin**: Username/password authentication
- **Database**: Local access only (localhost:5432)
- **Web Access**: HTTPS only (HTTP redirects to HTTPS)

---

## 📁 File Locations

### Key Configuration Files
```bash
# Odoo Configuration
/etc/odoo18.conf

# Nginx Configuration  
/etc/nginx/sites-available/kulturhaus-bortfeld.conf

# SSL Certificates
/etc/letsencrypt/live/kulturhaus-bortfeld.de/

# Log Files
/var/log/odoo/odoo18.log
/var/log/nginx/kulturhaus-access.log
/var/log/nginx/kulturhaus-error.log
```

### Application Directories
```bash
# Odoo Installation
/opt/odoo18/

# Database Data
/var/lib/postgresql/16/main/

# SSH Configuration
~/.ssh/authorized_keys
```

---

## 🔧 Common Operations

### Service Management
```bash
# Check all service status
ssh kulturhaus "systemctl status odoo18 nginx postgresql"

# Restart Odoo service
ssh kulturhaus "sudo systemctl restart odoo18"

# Check Odoo logs
ssh kulturhaus "sudo tail -f /var/log/odoo/odoo18.log"

# Check system resources
ssh kulturhaus "free -h && df -h"
```

### SSL Certificate Management
```bash
# Check certificate status
ssh kulturhaus "sudo certbot certificates"

# Test certificate renewal
ssh kulturhaus "sudo certbot renew --dry-run"
```

### Database Operations
```bash
# Connect to database
ssh kulturhaus "sudo -u odoo18 psql -d kulturhive"

# Database backup
ssh kulturhaus "sudo -u postgres pg_dump kulturhive > backup_$(date +%Y%m%d).sql"
```

---

## 📊 Monitoring & Health

### Health Check Commands
```bash
# Website availability
curl -I https://kulturhaus-bortfeld.de

# Odoo application health
ssh kulturhaus "curl -I http://localhost:8069"

# Database connectivity
ssh kulturhaus "sudo -u odoo18 psql -d kulturhive -c 'SELECT version();'"

# System resources
ssh kulturhaus "htop"
```

### Performance Metrics
- **Response Time**: <1 second typical
- **Memory Usage**: ~2.8GB/8GB used
- **Disk Usage**: 8.4GB/251GB used (3% full)
- **Worker Processes**: 8 Odoo workers active

---

## 🚨 Troubleshooting

### Common Issues & Quick Fixes

#### Website Not Responding
```bash
# Check nginx status
ssh kulturhaus "sudo systemctl status nginx"

# Restart nginx if needed
ssh kulturhaus "sudo systemctl restart nginx"
```

#### Odoo Performance Issues
```bash
# Check worker processes
ssh kulturhaus "ps aux | grep odoo18"

# Monitor resource usage
ssh kulturhaus "top -p $(pgrep -d, odoo18)"
```

#### SSL Certificate Issues
```bash
# Force certificate renewal
ssh kulturhaus "sudo certbot renew --force-renewal"
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
ssh kulturhaus "sudo systemctl status postgresql"

# Check database connections
ssh kulturhaus "sudo -u postgres psql -c \"SELECT datname, numbackends FROM pg_stat_database;\""
```

---

## 📋 Maintenance Schedule

### Regular Tasks
- **Daily**: Monitor system logs and performance
- **Weekly**: Review security logs and resource usage
- **Monthly**: System updates and security patches
- **Quarterly**: Full backup verification and disaster recovery test

### Automated Tasks
- ✅ **SSL Renewal**: Automatic via certbot
- ✅ **Log Rotation**: System-managed log rotation
- 🔄 **Database Backups**: Needs setup (recommended daily)
- 🔄 **System Updates**: Consider unattended-upgrades

---

## 🔄 Development Workflow

### Working with the Server
1. **Connect**: `ssh kulturhaus`
2. **Check Status**: Verify all services running
3. **Make Changes**: Edit configurations as needed
4. **Test**: Verify changes work correctly
5. **Document**: Update this CLAUDE.md if configurations change

### Configuration Changes
- Always backup configurations before changes
- Test changes in staging first (if available)
- Document all changes in version control
- Monitor logs after changes

---

## 📞 Support Information

### Technical Contacts
- **Primary Admin**: khaus (SSH access)
- **Server Provider**: LuckySrv
- **Domain Registrar**: TBD
- **SSL Provider**: Let's Encrypt (free)

### Emergency Procedures
1. **Server Down**: Check LuckySrv status page
2. **SSL Issues**: Force certificate renewal
3. **Database Issues**: Check PostgreSQL logs
4. **Performance Issues**: Check system resources

---

## 🎯 Project Goals & Next Steps

### Current Status: ✅ COMPLETE
- ✅ Server infrastructure setup
- ✅ Odoo 18 ERP system operational
- ✅ SSL certificates and security configured
- ✅ Domain and DNS properly configured
- ✅ Multi-worker performance optimization
- ✅ Monitoring and logging setup

### Future Enhancements
- [ ] Automated database backup system
- [ ] Application performance monitoring
- [ ] User training and documentation
- [ ] Custom Odoo modules (if needed)
- [ ] Integration with external systems
- [ ] Disaster recovery procedures

---

## 📚 Documentation References

### Project Documentation
- **Technical Documentation**: `TECHNICAL_DOCUMENTATION.md` (comprehensive server details)
- **Server Info**: `server-info.md` (basic server information)
- **SSH Setup**: `ssh-setup.md` (SSH configuration history)
- **IP Whitelist**: `ip-whitelist-config.md` (security configuration)

### External References
- **Odoo Documentation**: https://www.odoo.com/documentation/18.0/
- **Ubuntu Server Guide**: https://ubuntu.com/server/docs
- **Nginx Documentation**: https://nginx.org/en/docs/
- **Let's Encrypt**: https://letsencrypt.org/docs/

---

## ⚡ Quick Reference

### Most Used Commands
```bash
# SSH into server
ssh kulturhaus

# Check service status
ssh kulturhaus "systemctl status odoo18 nginx postgresql"

# View Odoo logs
ssh kulturhaus "sudo tail -f /var/log/odoo/odoo18.log"

# Check website
curl -I https://kulturhaus-bortfeld.de

# Monitor resources
ssh kulturhaus "htop"
```

### Important URLs
- **Production Website**: https://kulturhaus-bortfeld.de
- **Server IP**: http://193.30.120.108 (redirects to HTTPS)
- **Server Hostname**: v2202411240735294743.luckysrv.de

---

## 🏁 Project Status Summary

**🎉 PROJECT COMPLETE - PRODUCTION READY**

The Kulturhaus Bortfeld e.V. server is fully operational with:
- ✅ Complete Odoo 18 ERP system
- ✅ Secure HTTPS website with SSL
- ✅ Professional production configuration
- ✅ Security hardening and monitoring
- ✅ Performance optimization
- ✅ Comprehensive documentation

**System is ready for business use.**

---

*Last Updated: 2025-06-12 by Claude Code*  
*Status: Production Operational*