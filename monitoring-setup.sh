#!/bin/bash
# Kulturhaus VPS Monitoring Setup Script

echo "🔍 Setting up monitoring for Kulturhaus VPS..."

# Server details
SERVER="193.30.120.108"
USER="khaus"
SSH_KEY="$HOME/.ssh/kulturhaus_vps"

# Set SUDO_PASSWORD environment variable before running this script
# Example: SUDO_PASSWORD='your_password' ./monitoring-setup.sh
if [ -z "$SUDO_PASSWORD" ]; then
    echo "Error: SUDO_PASSWORD environment variable not set"
    echo "Usage: SUDO_PASSWORD='your_password' $0"
    exit 1
fi

# Install monitoring tools
ssh -i $SSH_KEY $USER@$SERVER << 'EOF'
echo "$SUDO_PASSWORD" | sudo -S bash -c '
# Install monitoring packages
apt-get update
apt-get install -y htop iotop nethogs vnstat

# Enable vnstat for network monitoring
systemctl enable vnstat
systemctl start vnstat

# Install netdata for comprehensive monitoring
wget -O /tmp/netdata-kickstart.sh https://get.netdata.cloud/kickstart.sh
bash /tmp/netdata-kickstart.sh --non-interactive --stable-channel

# Create simple monitoring script
cat > /usr/local/bin/server-health.sh << "SCRIPT"
#!/bin/bash
echo "=== Server Health Report ==="
echo "Date: $(date)"
echo ""
echo "=== System Load ==="
uptime
echo ""
echo "=== Memory Usage ==="
free -h
echo ""
echo "=== Disk Usage ==="
df -h /
echo ""
echo "=== Top Processes ==="
ps aux | head -10
echo ""
echo "=== Service Status ==="
systemctl is-active nginx odoo18 postgresql fail2ban docker
echo ""
echo "=== Recent Auth Logs ==="
tail -5 /var/log/auth.log | grep -E "(Failed|Accepted)"
echo ""
echo "=== UFW Status ==="
ufw status numbered | head -10
SCRIPT

chmod +x /usr/local/bin/server-health.sh

# Add daily health report to cron
(crontab -l 2>/dev/null; echo "0 8 * * * /usr/local/bin/server-health.sh > /var/log/daily-health.log 2>&1") | crontab -

# Create alert script for critical issues
cat > /usr/local/bin/alert-check.sh << "ALERT"
#!/bin/bash
# Check disk space
DISK_USAGE=$(df / | awk "NR==2 {print \$5}" | sed "s/%//")
if [ $DISK_USAGE -gt 80 ]; then
    echo "WARNING: Disk usage is at ${DISK_USAGE}%" | mail -s "Kulturhaus VPS Alert" it@kulturhaus-bortfeld.de
fi

# Check memory
MEM_USAGE=$(free | awk "NR==2 {print int(\$3/\$2*100)}")
if [ $MEM_USAGE -gt 90 ]; then
    echo "WARNING: Memory usage is at ${MEM_USAGE}%" | mail -s "Kulturhaus VPS Alert" it@kulturhaus-bortfeld.de
fi

# Check services
for service in nginx odoo18 postgresql fail2ban docker; do
    if ! systemctl is-active --quiet $service; then
        echo "CRITICAL: Service $service is not running!" | mail -s "Kulturhaus VPS Alert" it@kulturhaus-bortfeld.de
    fi
done
ALERT

chmod +x /usr/local/bin/alert-check.sh

# Add hourly alert check
(crontab -l 2>/dev/null; echo "0 * * * * /usr/local/bin/alert-check.sh") | crontab -

echo "✅ Monitoring setup complete!"
echo "📊 Netdata Web UI will be available at: http://193.30.120.108:19999"
echo "📧 Alerts will be sent to: it@kulturhaus-bortfeld.de"
'
EOF

echo "
=== Monitoring Setup Complete ===

Access monitoring tools:
1. Netdata Web UI: http://$SERVER:19999
2. SSH to server and run: server-health.sh
3. View logs: /var/log/daily-health.log

Monitoring includes:
- System resources (CPU, RAM, Disk)
- Network traffic (vnstat)
- Service health checks
- Security alerts (failed logins)
- Automatic alerts for critical issues
"