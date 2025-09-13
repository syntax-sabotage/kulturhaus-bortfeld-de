# Vaultwarden Passwortmanager - Kulturhaus Bortfeld

## 🔐 Zugang
- **URL**: https://sec.kulturhausbortfeld.de (DNS noch konfigurieren!)
- **Admin Panel**: https://sec.kulturhausbortfeld.de/admin
- **Admin Token**: `+K96pl/beeoCxMh0YAufUbaYkSupG25QRO+F2iu1ZOnyGpdV1u/lyqDkbareQT9N`

## 📍 Server Details
- **Server**: VPS 193.30.120.108
- **Verzeichnis**: `/home/khaus/vaultwarden/`
- **Docker Container**: vaultwarden
- **Port**: 3012 (intern) → 443 (extern via Nginx)

## 🚀 Status
- ✅ Docker installiert und läuft
- ✅ Vaultwarden Container aktiv
- ✅ Nginx Reverse Proxy konfiguriert
- ✅ fail2ban Schutz aktiv
- ✅ Backup-System eingerichtet (täglich 2:00 Uhr)
- ⏳ Warte auf DNS-Konfiguration bei Strato

## 📝 DNS Konfiguration (Bei Strato)
```
Type: A
Name: sec
Host: kulturhausbortfeld.de
Wert: 193.30.120.108
TTL: 300
```

## 🔧 Administration

### Container Management
```bash
ssh khaus@193.30.120.108
cd ~/vaultwarden

# Status prüfen
docker-compose ps

# Logs ansehen
docker-compose logs -f

# Neustart
docker-compose restart

# Stoppen
docker-compose down

# Starten
docker-compose up -d
```

### Backup & Restore
```bash
# Manuelles Backup
./backup-vaultwarden.sh

# Restore (mit Timestamp)
./restore-vaultwarden.sh 20250913_160000

# Backups ansehen
ls -la backups/
```

### Benutzer einladen
1. Admin Panel öffnen: https://sec.kulturhausbortfeld.de/admin
2. Admin Token eingeben
3. "Invite User" → E-Mail eingeben
4. Einladungslink wird per Mail verschickt

## 🛡️ Sicherheit
- Public Signups: DEAKTIVIERT
- Nur Einladungen möglich
- Admin Panel geschützt
- HTTPS only
- fail2ban aktiv
- Rate Limiting konfiguriert

## 📊 Wichtige Dateien
```
~/vaultwarden/
├── docker-compose.yml          # Hauptkonfiguration
├── .env                        # Umgebungsvariablen
├── data/                       # Vaultwarden Daten
├── backups/                    # Backup-Verzeichnis
├── backup-vaultwarden.sh       # Backup-Script
├── restore-vaultwarden.sh      # Restore-Script
└── VAULTWARDEN_ADMINISTRATION_GUIDE.md
```

## ⚠️ Nach DNS-Aktivierung

1. **Let's Encrypt SSL installieren:**
```bash
sudo certbot certonly --webroot -w /var/www/html -d sec.kulturhausbortfeld.de
```

2. **Nginx SSL-Pfade updaten:**
```bash
sudo nano /etc/nginx/sites-available/sec.kulturhausbortfeld.conf
# Pfade ändern zu:
ssl_certificate /etc/letsencrypt/live/sec.kulturhausbortfeld.de/fullchain.pem;
ssl_certificate_key /etc/letsencrypt/live/sec.kulturhausbortfeld.de/privkey.pem;
```

3. **Nginx neuladen:**
```bash
sudo nginx -t
sudo systemctl reload nginx
```

## 📱 Apps für Nutzer
- **iOS/Android**: Bitwarden App
- **Desktop**: Bitwarden Desktop
- **Browser**: Bitwarden Extension
- Server URL: `https://sec.kulturhausbortfeld.de`

---
**Installation**: 13.09.2025
**Status**: Bereit, wartet auf DNS