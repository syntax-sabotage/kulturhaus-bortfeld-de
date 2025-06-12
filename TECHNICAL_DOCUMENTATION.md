# Kulturhaus Bortfeld e.V. - Technical Server Documentation

**Version**: 1.0  
**Date**: 2025-06-12  
**Status**: ✅ PRODUCTION READY  
**Environment**: Production Server  

---

## 📋 Executive Summary

The Kulturhaus Bortfeld e.V. server is a **fully operational production environment** running Odoo 18 ERP system with complete web infrastructure. All services are running optimally with proper security configurations.

**🌐 Live System**: https://kulturhaus-bortfeld.de

---

## 🖥️ Server Infrastructure

### Hardware Specifications
- **Provider**: LuckySrv
- **Hostname**: v2202411240735294743.luckysrv.de
- **IP Address**: 193.30.120.108
- **RAM**: 8GB (7.8GB total, 5.0GB available)
- **Storage**: 251GB SSD (233GB available)
- **CPU**: Multi-core (exact specs TBD)

### Operating System
- **OS**: Ubuntu 24.04.1 LTS (Noble)
- **Kernel**: Linux (exact version via `uname -r`)
- **Architecture**: x64
- **Last Update**: Current as of deployment

---

## 🔐 Security Configuration

### SSH Access
- **SSH User**: `khaus`
- **SSH Password**: `Basf1$Khaus`
- **SSH Port**: 22 (standard)
- **Key Authentication**: ✅ Enabled (ed25519)
- **Password Authentication**: ✅ Enabled (backup method)

### SSH Key Details
```
Type: ssh-ed25519
Fingerprint: SHA256:ZMOeN/i4qliEVRCaJFhH+x895KwSuNqJKt9ORPX0CdU
Comment: kulturhaus-bortfeld-ev-server
Location: ~/.ssh/kulturhaus_bortfeld
```

### IP Whitelisting
- **Whitelisted IP**: 94.31.75.76
- **Method**: fail2ban ignoreip configuration
- **Configuration**: `/etc/fail2ban/jail.local`

### Firewall Configuration
- **Service**: UFW (Ubuntu Firewall)
- **SSH Access**: ✅ Allowed
- **HTTP/HTTPS**: ✅ Allowed through nginx
- **Database**: 🔒 Local access only

---

## 🗄️ Database Configuration

### PostgreSQL 16
- **Version**: PostgreSQL 16/main
- **Port**: 5432 (localhost only)
- **Admin User**: postgres
- **Odoo User**: odoo18
- **Odoo Password**: khaus

### Database Details
- **Database Name**: kulturhive
- **Owner**: odoo18
- **Encoding**: UTF8 (standard)
- **Connection Limit**: Multiple worker connections active
- **Backup Schedule**: TBD (recommended: daily automated backups)

### Active Connections
```bash
# Multiple active connections to kulturhive database
postgres: 16/main: odoo18 kulturhive 127.0.0.1(48140) idle
postgres: 16/main: odoo18 kulturhive 127.0.0.1(48146) idle
postgres: 16/main: odoo18 kulturhive 127.0.0.1(48150) idle
```

---

## 🚀 Odoo 18 ERP Configuration

### Installation Details
- **Version**: Odoo 18 (latest stable)
- **Installation Path**: `/opt/odoo18/`
- **Python Version**: Python 3.12
- **Virtual Environment**: `/opt/odoo18/odoo/venv/`
- **User**: odoo18
- **Group**: odoo18

### Service Configuration
- **Service Name**: odoo18.service
- **Configuration File**: `/etc/odoo18.conf`
- **Log File**: `/var/log/odoo/odoo18.log`
- **Status**: ✅ Active (running since Wed 2025-06-11 21:47:17 CEST)

### Odoo Configuration (`/etc/odoo18.conf`)
```ini
[options]
db_host = localhost
db_port = 5432
db_user = odoo18
db_password = khaus
addons_path = /opt/odoo18/odoo/addons
default_productivity_apps = True
logfile = /var/log/odoo/odoo18.log
admin_passwd = khaus
proxy_mode = True
max_cron_threads = 1
workers = 8
longpolling_port = False
gevent_port = 8072
```

### Worker Configuration
- **Worker Processes**: 8 (multi-worker setup)
- **Memory Usage**: 2.4GB total across all workers
- **Gevent Port**: 8072 (for WebSocket/real-time features)
- **Proxy Mode**: ✅ Enabled (for nginx reverse proxy)

### Performance Optimization
- **Worker Architecture**: Multi-process for concurrent user handling
- **Cron Threads**: 1 (optimized for server resources)
- **Memory Allocation**: ~300MB per worker process
- **Database Connection Pooling**: Active

---

## 🌐 Web Server Configuration

### Nginx Reverse Proxy
- **Version**: nginx/1.24.0 (Ubuntu)
- **Configuration**: `/etc/nginx/sites-available/kulturhaus-bortfeld.conf`
- **Status**: ✅ Active with 4 worker processes
- **SSL Termination**: ✅ Configured

### Domain Configuration
- **Primary Domain**: kulturhaus-bortfeld.de
- **Alias**: www.kulturhaus-bortfeld.de
- **HTTP Redirect**: ✅ All HTTP traffic redirected to HTTPS
- **WebSocket Support**: ✅ Configured for Odoo real-time features

### SSL/TLS Configuration
- **Certificate Authority**: Let's Encrypt
- **Certificate Path**: `/etc/letsencrypt/live/kulturhaus-bortfeld.de/`
- **Certificate Status**: ✅ Valid and active
- **Auto-Renewal**: ✅ Configured (via certbot)

### Nginx Configuration Details
```nginx
# Upstream-Definition für Odoo Backend
upstream odoo {
    server 127.0.0.1:8069;
}

# WebSocket-Verbindung für z.B. Discuss-App
upstream odoo_chat {
    server 127.0.0.1:8072;
}

# HTTPS-Serverblock für Odoo-Reverse-Proxy
server {
    listen 443 ssl;
    server_name kulturhaus-bortfeld.de www.kulturhaus-bortfeld.de;
    
    ssl_certificate /etc/letsencrypt/live/kulturhaus-bortfeld.de/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/kulturhaus-bortfeld.de/privkey.pem;
    
    proxy_read_timeout 720s;
    proxy_connect_timeout 720s;
    proxy_send_timeout 720s;
    client_max_body_size 100M;
    
    location / {
        proxy_pass http://odoo;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto https;
    }
    
    location /websocket {
        proxy_pass http://odoo_chat;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection $connection_upgrade;
    }
}
```

---

## 📊 Service Status Overview

### Active Services
| Service | Status | Port | Purpose |
|---------|--------|------|---------|
| **odoo18** | ✅ Active | 8069 | Main ERP Application |
| **postgresql-16** | ✅ Active | 5432 | Database Server |
| **nginx** | ✅ Active | 80/443 | Web Server/Reverse Proxy |
| **ssh** | ✅ Active | 22 | Remote Administration |
| **fail2ban** | ✅ Active | - | Intrusion Prevention |

### System Resources
- **CPU Usage**: Low (optimized multi-worker setup)
- **Memory Usage**: 2.8GB used / 7.8GB total (65% available)
- **Disk Usage**: 8.4GB used / 251GB total (93% available)
- **Network**: All services responding normally

---

## 🔧 Maintenance & Operations

### Regular Maintenance Tasks
1. **Daily**: Monitor system logs and performance
2. **Weekly**: Review security logs and fail2ban reports
3. **Monthly**: Update system packages and security patches
4. **Quarterly**: Review and update SSL certificates (auto-renewal active)

### Backup Strategy (Recommended)
```bash
# Database backup (daily recommended)
sudo -u postgres pg_dump kulturhive > backup_$(date +%Y%m%d).sql

# Odoo filestore backup
tar -czf odoo_filestore_$(date +%Y%m%d).tar.gz /opt/odoo18/odoo/filestore/

# Configuration backup
tar -czf config_backup_$(date +%Y%m%d).tar.gz /etc/odoo18.conf /etc/nginx/sites-available/
```

### Log Locations
- **Odoo Logs**: `/var/log/odoo/odoo18.log`
- **Nginx Access**: `/var/log/nginx/kulturhaus-access.log`
- **Nginx Error**: `/var/log/nginx/kulturhaus-error.log`
- **System Logs**: `/var/log/syslog`
- **SSH Logs**: `/var/log/auth.log`

---

## 🚨 Troubleshooting Guide

### Common Issues & Solutions

#### Odoo Service Issues
```bash
# Check service status
sudo systemctl status odoo18

# Restart service
sudo systemctl restart odoo18

# View recent logs
sudo tail -f /var/log/odoo/odoo18.log
```

#### Database Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Test database connection
sudo -u odoo18 psql -h localhost -d kulturhive -U odoo18
```

#### SSL Certificate Issues
```bash
# Check certificate status
sudo certbot certificates

# Renew certificates
sudo certbot renew --dry-run
```

#### Performance Issues
```bash
# Monitor system resources
htop
free -h
df -h

# Check Odoo worker processes
ps aux | grep odoo18
```

---

## 📈 Performance Monitoring

### Key Metrics to Monitor
- **Response Time**: Target <2 seconds for typical pages
- **Memory Usage**: Keep below 6GB total usage
- **Database Connections**: Monitor for connection leaks
- **SSL Certificate Expiry**: Auto-renewal should prevent issues
- **Disk Space**: Alert when >85% full

### Monitoring Commands
```bash
# Real-time system monitoring
htop

# Check Odoo performance
curl -w "@curl-format.txt" -o /dev/null -s https://kulturhaus-bortfeld.de

# Database performance
sudo -u postgres psql -c "SELECT datname, numbackends, conflicts, deadlocks FROM pg_stat_database WHERE datname='kulturhive';"
```

---

## 🔄 Deployment Information

### Current Deployment
- **Deployment Date**: 2025-06-11
- **Deployment Method**: Manual installation and configuration
- **Environment**: Production
- **Last Update**: 2025-06-12

### Version Information
- **Odoo**: 18 (latest stable)
- **PostgreSQL**: 16
- **Python**: 3.12.3
- **Nginx**: 1.24.0
- **Ubuntu**: 24.04.1 LTS

---

## 📞 Support & Contacts

### Technical Support
- **Primary Admin**: khaus user
- **SSH Access**: Via key authentication
- **Emergency Access**: Password authentication available

### Service Provider
- **Hosting**: LuckySrv
- **Domain**: kulturhaus-bortfeld.de
- **SSL**: Let's Encrypt (auto-renewal)

---

## ✅ System Health Check

**Last Verified**: 2025-06-12 07:30 CET

| Component | Status | Response Time | Last Check |
|-----------|--------|---------------|------------|
| **Website** | ✅ Online | <500ms | 2025-06-12 07:30 |
| **Odoo Login** | ✅ Working | <1s | 2025-06-12 07:30 |
| **Database** | ✅ Connected | <100ms | 2025-06-12 07:30 |
| **SSL Certificate** | ✅ Valid | - | 2025-06-12 07:30 |
| **SSH Access** | ✅ Working | <200ms | 2025-06-12 07:30 |

---

## 📋 Next Steps & Recommendations

### Immediate Actions Required
- [ ] Set up automated database backups
- [ ] Configure monitoring alerts
- [ ] Document admin user credentials for Odoo
- [ ] Set up log rotation for Odoo logs

### Future Enhancements
- [ ] Implement database clustering for high availability
- [ ] Add application performance monitoring
- [ ] Set up automated security updates
- [ ] Configure backup verification procedures

---

*This documentation is maintained by the Kulturhaus Bortfeld e.V. technical team. Last updated: 2025-06-12*