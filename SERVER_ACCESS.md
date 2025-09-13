# Server Access Documentation - Kulturhaus Bortfeld

## 🔐 Zugangsinformationen

### VPS Server
- **IP**: 193.30.120.108
- **User**: khaus
- **SSH-Key**: `~/.ssh/kulturhaus_vps`
- **Passwort**: In 1Password gespeichert

### SSH Verbindung
```bash
# Mit SSH-Key (empfohlen)
ssh -i ~/.ssh/kulturhaus_vps khaus@193.30.120.108

# Alternative (falls Key nicht funktioniert)
ssh khaus@193.30.120.108
```

## 🌐 Web-Services

### Hauptwebsite
- **URL**: https://kulturhaus-bortfeld.de
- **Odoo Admin**: admin / (in 1Password)

### Vaultwarden Passwortmanager
- **URL**: https://sec.kulturhausbortfeld.de
- **Admin Panel**: https://sec.kulturhausbortfeld.de/admin
- **Admin Token**: In `.env` auf Server oder 1Password

### Monitoring
- **Netdata**: http://193.30.120.108:19999
- **Zugang**: Öffentlich (Read-Only)

## 📧 E-Mail Benachrichtigungen
Alle System-Benachrichtigungen gehen an: **it@kulturhaus-bortfeld.de**

## 🔒 Sicherheit
- Root-Login: **Deaktiviert**
- Firewall: **UFW aktiv**
- Automatische Updates: **Aktiviert**
- Monitoring: **Netdata + Custom Scripts**
- Backups: **Täglich automatisch**

## 🚀 Wichtige Befehle

### Service Management
```bash
# Odoo
sudo systemctl status odoo18
sudo systemctl restart odoo18

# Vaultwarden
cd ~/vaultwarden
docker-compose ps
docker-compose restart

# Nginx
sudo systemctl status nginx
sudo systemctl reload nginx
```

### Backups
```bash
# Vaultwarden Backup
cd ~/vaultwarden
./backup-vaultwarden.sh

# Kulturhaus Backup
cd ~
./scripts/backup.sh manual
```

### Monitoring
```bash
# Server Health Check
/usr/local/bin/server-health.sh

# Live Monitoring
htop  # CPU/RAM
iotop # Disk I/O
nethogs # Network
```

## 📝 Hinweise
- Passwörter NIEMALS in Git committen
- Sensible Daten in 1Password speichern
- Bei Problemen: it@kulturhaus-bortfeld.de kontaktieren