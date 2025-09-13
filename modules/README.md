# Kulturhaus Bortfeld - Custom Odoo Modules

Diese Module sind speziell für das Kulturhaus Bortfeld e.V. entwickelt und erweitern die Odoo 18 Community Edition.

## 📦 Module Übersicht

### 1. kulturhaus_membership_sepa
**SEPA-Lastschrift für Mitgliedschaften**
- SEPA-Mandate verwaltung
- Konfigurierbare Mitgliedschaftszeiträume (Ganz-/Halbjahr)
- Batch-Generierung für Lastschriften
- SEPA XML Export für Banken

### 2. kulturhaus_dashboard
**Custom Dashboard für Kulturhaus**
- Personalisierte Übersichtsseiten
- Konfigurierbare Dashboard-Karten
- Schnellzugriff auf wichtige Funktionen
- Statistiken und Kennzahlen

### 3. kulturhaus_calendar_subscription
**Kalender-Abonnement Features**
- iCal Feed Generation
- Persönliche Kalender-URLs
- Automatische Event-Synchronisation
- Token-basierte Authentifizierung

### 4. kulturhaus_simplified_checkout
**Vereinfachter Checkout-Prozess**
- Optimierter Event-Ticketverkauf
- Deutsche Adress-Autovervollständigung
- Minimalistisches Checkout-Design
- Mobile-optimiert

### 5. kh_menu_organizer
**Menü-Organisation Tool**
- Odoo Menüstruktur anpassen
- Benutzerfreundliche Navigation
- Rollen-basierte Menüanzeige
- Vereinfachte Benutzererfahrung

## 🚀 Installation

1. Module in Odoo Addons-Verzeichnis kopieren:
```bash
sudo cp -r modules/* /opt/odoo18/odoo/addons/
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kulturhaus_*
sudo chown -R odoo18:odoo18 /opt/odoo18/odoo/addons/kh_*
```

2. Odoo neustarten:
```bash
sudo systemctl restart odoo18
```

3. Module in Odoo aktivieren:
   - Apps → Module aktualisieren
   - Nach "kulturhaus" suchen
   - Module installieren

## 🔧 Konfiguration

### SEPA Modul
- Einstellungen → Kulturhaus → SEPA Einstellungen
- Gläubiger-ID eintragen
- Bankverbindung konfigurieren

### Dashboard
- Einstellungen → Benutzer → Dashboard konfigurieren
- Karten-Layout anpassen
- Zugriffsrechte vergeben

### Calendar Subscription
- Automatisch nach Installation verfügbar
- Benutzer können persönliche Kalender-URLs generieren

## 📝 Entwicklung

### Voraussetzungen
- Odoo 18.0 Community Edition
- Python 3.10+
- PostgreSQL 12+

### Module aktualisieren
```bash
./odoo-bin -u module_name -d database_name
```

### Neue Features
Pull Requests bitte an: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de

## 📄 Lizenz

Diese Module sind proprietär für Kulturhaus Bortfeld e.V.
Weitergabe nur mit schriftlicher Genehmigung.

## 🤝 Support

Bei Fragen oder Problemen:
- GitHub Issues: https://github.com/syntax-sabotage/kulturhaus-bortfeld-de/issues
- E-Mail: support@kulturhaus-bortfeld.de