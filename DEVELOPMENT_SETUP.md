# Kulturhaus Entwicklungsumgebung - Docker Setup

## 🚀 Quick Start

```bash
cd /Users/larsweiler/Development/docker-environments/kulturhaus-dev
docker-compose up -d
```

**Zugriff:** http://localhost:8070  
**Login:** admin / admin  
**Datenbank:** kulturhaus_dev

## 📦 Installierte Module

Die folgenden Kulturhaus-Module sind jetzt in der Docker-Umgebung verfügbar:

### 1. kulturhaus_membership_sepa
- SEPA-Lastschrift für Mitgliedschaften
- Mandate verwaltung
- Batch-Generierung

### 2. kulturhaus_dashboard  
- Custom Dashboard
- Konfigurierbare Karten
- Statistiken

### 3. kulturhaus_calendar_subscription
- iCal Feeds
- Token-basierte Authentifizierung
- Event-Synchronisation

### 4. kulturhaus_simplified_checkout
- Optimierter Event-Checkout
- Deutsche Adressvervollständigung
- Mobile-optimiert

### 5. kh_menu_organizer
- Menü-Anpassung
- Benutzerfreundliche Navigation

### 6. mitmach_portal
- Volunteer Management
- Schichtplanung
- QR Check-in/out

## 🔧 Module aktivieren

1. Browser öffnen: http://localhost:8070
2. Login: admin / admin
3. Apps → Module aktualisieren
4. Nach "kulturhaus" oder "mitmach" suchen
5. Module installieren

## 📝 Entwicklung

### Module bearbeiten
```bash
cd /Users/larsweiler/Development/docker-environments/kulturhaus-dev/addons
# Module direkt hier bearbeiten
```

### Änderungen testen
```bash
# Container neustarten für Code-Änderungen
docker-compose restart kulturhaus-odoo

# Oder mit --dev=all für Auto-Reload (bereits aktiviert)
docker logs -f kulturhaus-odoo
```

### Module upgraden
```bash
docker exec kulturhaus-odoo python3 /usr/bin/odoo \
  -u module_name -d kulturhaus_dev
```

## 🐛 Debugging

### Logs anzeigen
```bash
docker logs -f kulturhaus-odoo
```

### In Container einloggen
```bash
docker exec -it kulturhaus-odoo bash
```

### Datenbank zugreifen
```bash
docker exec -it kulturhaus-db psql -U odoo18 -d kulturhaus_dev
```

## 🔄 Sync mit Production

### Module von Production holen
```bash
sshpass -p 'Basf1$Khaus' scp -r khaus@193.30.120.108:/opt/odoo18/odoo/addons/module_name ./addons/
```

### Module zu Production deployen
```bash
sshpass -p 'Basf1$Khaus' scp -r ./addons/module_name khaus@193.30.120.108:/opt/odoo18/odoo/addons/
ssh khaus@193.30.120.108 "sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/module_name"
ssh khaus@193.30.120.108 "sudo systemctl restart odoo18"
```

## 📋 Docker Commands

```bash
# Start
docker-compose up -d

# Stop
docker-compose down

# Restart
docker-compose restart

# Status
docker-compose ps

# Logs
docker-compose logs -f

# Clean restart (Datenbank bleibt)
docker-compose down && docker-compose up -d

# Full reset (ACHTUNG: Löscht alle Daten!)
docker-compose down -v && docker-compose up -d
```

## 🎯 Nächste Schritte

1. ✅ Module sind kopiert und gemountet
2. ✅ Docker läuft mit Odoo 18
3. ⏳ Module in Odoo UI installieren
4. ⏳ Membership SEPA Enhancements entwickeln

---
**Entwicklungsumgebung bereit für Kulturhaus Module!**