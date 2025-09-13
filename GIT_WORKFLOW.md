# Git Workflow für Kulturhaus Module

## 🌳 Branch-Strategie

```
main (production)     → VPS Server (193.30.120.108)
  ↑
  │ Pull Request (nach Review)
  │
develop              → Docker Lokal (localhost:8070)
  ↑
  │ Merge
  │
feature/xxx          → Feature-Entwicklung
hotfix/xxx           → Kritische Fixes
```

## 📋 Workflow

### 1. Feature entwickeln
```bash
# Neuen Feature-Branch erstellen
git checkout develop
git pull origin develop
git checkout -b feature/membership-improvements

# Entwickeln und testen in Docker
# Code bearbeiten in addons/kulturhaus_membership_sepa/

# Änderungen committen
git add .
git commit -m "feat: Add automatic SEPA batch generation"

# Feature-Branch pushen
git push origin feature/membership-improvements
```

### 2. Pull Request erstellen
- GitHub: Create Pull Request
- Base: `develop` ← Compare: `feature/xxx`
- Review anfordern
- Tests durchführen

### 3. Zu Develop mergen
```bash
git checkout develop
git merge feature/membership-improvements
git push origin develop
```

### 4. Production Release
```bash
# Wenn develop stabil ist
git checkout main
git merge develop
git push origin main

# Auf VPS deployen
ssh khaus@193.30.120.108
cd /opt/kulturhaus-docs
git pull origin main
# Module zu Odoo kopieren und neustarten
```

## 🔄 Sync-Befehle

### Lokale Entwicklung starten
```bash
cd /Users/larsweiler/Development/docker-environments/kulturhaus-dev
git checkout develop
git pull origin develop
docker-compose up -d
```

### Module von Production holen
```bash
# Falls auf Production direkt geändert wurde
git checkout main
git pull origin main
git checkout develop
git merge main
```

### Hotfix deployen
```bash
git checkout -b hotfix/critical-fix main
# Fix implementieren
git commit -m "fix: Critical SEPA export issue"
git push origin hotfix/critical-fix

# Nach Review
git checkout main
git merge hotfix/critical-fix
git push origin main

# Auch zu develop
git checkout develop
git merge hotfix/critical-fix
git push origin develop
```

## 📁 Verzeichnis-Struktur

```
docker-environments/kulturhaus-dev/  (develop branch)
├── modules/                         # Symlink oder Kopie
│   ├── kulturhaus_membership_sepa/
│   └── ...
├── addons/                          # Docker mount point
│   └── ... (selbe Module)
└── docker-compose.yml

GitHub Repository:
├── modules/                         # Source of truth
│   ├── kulturhaus_membership_sepa/
│   └── ...
├── scripts/
└── configurations/
```

## ⚠️ Wichtige Regeln

1. **NIEMALS** direkt auf `main` entwickeln
2. **IMMER** über Pull Requests zu `main`
3. **Docker** nutzt `develop` branch
4. **VPS** nutzt `main` branch
5. **Features** immer von `develop` branchen
6. **Hotfixes** immer von `main` branchen

## 🚀 Quick Commands

```bash
# Status prüfen
git status
git branch -a

# Aktuellen Branch updaten
git pull

# Neuen Feature-Branch
git checkout -b feature/neue-funktion

# Änderungen pushen
git add .
git commit -m "feat: Beschreibung"
git push origin feature/neue-funktion

# PR erstellen
# → Über GitHub UI

# Nach PR-Merge aufräumen
git checkout develop
git pull
git branch -d feature/neue-funktion
```

---
**Aktueller Status:**
- ✅ Repository geklont
- ✅ Develop branch erstellt
- ✅ Module in Docker verfügbar
- 🔄 Bereit für Entwicklung!