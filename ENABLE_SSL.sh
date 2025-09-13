#!/bin/bash
# Script zum Aktivieren von Let's Encrypt SSL für Vaultwarden
# Nach DNS-Konfiguration ausführen!

echo "🔐 Aktiviere SSL für sec.kulturhausbortfeld.de"

# Auf VPS verbinden und SSL einrichten
ssh khaus@193.30.120.108 << 'EOF'
echo "📍 Teste DNS-Auflösung..."
host sec.kulturhausbortfeld.de

echo "🔒 Installiere Let's Encrypt Zertifikat..."
sudo certbot certonly --nginx -d sec.kulturhausbortfeld.de --non-interactive --agree-tos -m it@kulturhaus-bortfeld.de

echo "✏️ Update Nginx Konfiguration..."
sudo sed -i 's|/etc/ssl/vaultwarden/cert.pem|/etc/letsencrypt/live/sec.kulturhausbortfeld.de/fullchain.pem|g' /etc/nginx/sites-available/sec.kulturhausbortfeld.conf
sudo sed -i 's|/etc/ssl/vaultwarden/key.pem|/etc/letsencrypt/live/sec.kulturhausbortfeld.de/privkey.pem|g' /etc/nginx/sites-available/sec.kulturhausbortfeld.conf

echo "🔄 Teste und lade Nginx neu..."
sudo nginx -t && sudo systemctl reload nginx

echo "✅ SSL aktiviert! Teste: https://sec.kulturhausbortfeld.de"
EOF

echo "📱 Konfiguration für Nutzer:"
echo "Server URL in Bitwarden App: https://sec.kulturhausbortfeld.de"
echo "Admin Panel: https://sec.kulturhausbortfeld.de/admin"