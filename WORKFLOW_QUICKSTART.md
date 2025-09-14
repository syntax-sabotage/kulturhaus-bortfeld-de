# 🚀 Kulturhaus Entwicklungs-Workflow - Quick Reference

## 📍 Wo bin ich?
```bash
pwd  # Sollte sein: /Users/larsweiler/Development/docker-environments/kulturhaus-dev
git branch  # Sollte zeigen: * develop
```

## 🔄 Täglicher Start
```bash
# 1. Docker starten
docker-compose up -d

# 2. Branch updaten
git pull origin develop

# 3. Browser öffnen
open http://localhost:8070
# Login: admin / admin
```

## 💻 Entwickeln

### Neues Feature starten
```bash
git checkout -b feature/mein-feature
# Entwickle in: addons/kulturhaus_membership_sepa/
```

### Code testen
```bash
# Odoo neu laden (automatisch mit --dev=all)
# Oder manuell:
docker-compose restart kulturhaus-odoo
```

### Feature fertig
```bash
git add .
git commit -m "feat: Beschreibung der Änderung"
git push origin feature/mein-feature
```

### Pull Request
1. Gehe zu: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de
2. Click "Compare & pull request"
3. Base: `develop` ← Compare: `feature/mein-feature`
4. Create Pull Request

## 🚨 Hotfix (Kritischer Bug)
```bash
git checkout -b hotfix/bug-fix main
# Fix machen
git commit -m "fix: Kritisches Problem gelöst"
git push origin hotfix/bug-fix
# PR zu main erstellen
```

## 📦 Module Management

### Neues Modul installieren
1. Browser: http://localhost:8070
2. Apps → Module aktualisieren
3. Suche: "kulturhaus"
4. Installieren

### Modul upgraden
```bash
docker exec kulturhaus-odoo python3 /usr/bin/odoo \
  -u kulturhaus_membership_sepa -d kulturhaus_dev
```

### Demo-Daten laden
```bash
# Script zum Laden der Demo-Daten (50 Mitglieder mit SEPA)
python3 scripts/upgrade_with_demo.py

# Status prüfen
python3 scripts/load_demo_data.py
```

## 🔍 Debugging

### Logs anzeigen
```bash
docker logs -f kulturhaus-odoo
```

### Python Shell
```bash
docker exec -it kulturhaus-odoo python3 /usr/bin/odoo shell -d kulturhaus_dev
```

### Datenbank zurücksetzen
```bash
docker-compose down -v  # ACHTUNG: Löscht alles!
docker-compose up -d
```

## 🚀 Deployment zu Production

### Nach PR-Merge zu main
```bash
# Auf VPS einloggen
ssh -i ~/.ssh/kulturhaus_vps khaus@193.30.120.108

# Module updaten
cd /opt/kulturhaus-docs
git pull origin main
sudo cp -r modules/* /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_*
sudo systemctl restart odoo18
```

## 📋 Cheat Sheet

| Aktion | Befehl |
|--------|--------|
| Docker starten | `docker-compose up -d` |
| Docker stoppen | `docker-compose down` |
| Logs anzeigen | `docker logs -f kulturhaus-odoo` |
| Branch wechseln | `git checkout develop` |
| Status prüfen | `git status` |
| Änderungen committen | `git add . && git commit -m "msg"` |
| Push zu GitHub | `git push origin branch-name` |
| Odoo URL | http://localhost:8070 |
| VPS URL | https://kulturhaus-bortfeld.de |

## 🎯 Goldene Regeln

1. **IMMER** auf `develop` oder Feature-Branch arbeiten
2. **NIE** direkt auf `main` pushen
3. **TESTE** lokal bevor du pushst
4. **PR** für alle Änderungen zu main
5. **BACKUP** vor kritischen Änderungen

---
**Quick Help:** `cat WORKFLOW_QUICKSTART.md`