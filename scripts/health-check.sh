#!/bin/bash

# Kulturhaus Bortfeld - System Health Check
# Usage: ./scripts/health-check.sh

echo "🏥 Kulturhaus Bortfeld - System Health Check"
echo "=============================================="
echo "Date: $(date)"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to check service status
check_service() {
    local service=$1
    if systemctl is-active --quiet $service; then
        echo -e "✅ ${GREEN}$service${NC} - Running"
        return 0
    else
        echo -e "❌ ${RED}$service${NC} - Not running"
        return 1
    fi
}

# Function to check URL response
check_url() {
    local url=$1
    local description=$2
    
    if curl -f -s -I "$url" > /dev/null; then
        echo -e "✅ ${GREEN}$description${NC} - Responding"
        return 0
    else
        echo -e "❌ ${RED}$description${NC} - Not responding"
        return 1
    fi
}

# Check system services
echo "🔧 System Services:"
check_service "odoo18"
check_service "postgresql"
check_service "nginx"
check_service "ssh"
echo ""

# Check web endpoints
echo "🌐 Web Services:"
check_url "https://kulturhaus-bortfeld.de" "Main website (HTTPS)"
check_url "http://localhost:8069" "Odoo application (local)"
echo ""

# Check system resources
echo "💾 System Resources:"

# Memory usage
MEMORY_USAGE=$(free | grep Mem | awk '{printf "%.1f", $3/$2 * 100.0}')
if (( $(echo "$MEMORY_USAGE > 80" | bc -l) )); then
    echo -e "⚠️  ${YELLOW}Memory usage${NC} - ${MEMORY_USAGE}% (High)"
else
    echo -e "✅ ${GREEN}Memory usage${NC} - ${MEMORY_USAGE}%"
fi

# Disk usage  
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 85 ]; then
    echo -e "⚠️  ${YELLOW}Disk usage${NC} - ${DISK_USAGE}% (High)"
else
    echo -e "✅ ${GREEN}Disk usage${NC} - ${DISK_USAGE}%"
fi

# Load average
LOAD_AVG=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | xargs)
echo -e "📊 ${GREEN}Load average${NC} - $LOAD_AVG"
echo ""

# Check database connectivity
echo "🗄️  Database:"
if sudo -u odoo18 psql -d kulturhive -c "SELECT version();" > /dev/null 2>&1; then
    echo -e "✅ ${GREEN}PostgreSQL connection${NC} - Working"
    
    # Count active connections
    CONN_COUNT=$(sudo -u postgres psql -t -c "SELECT count(*) FROM pg_stat_activity WHERE datname='kulturhive';" 2>/dev/null | xargs)
    echo -e "📊 ${GREEN}Active DB connections${NC} - $CONN_COUNT"
else
    echo -e "❌ ${RED}PostgreSQL connection${NC} - Failed"
fi
echo ""

# Check SSL certificate
echo "🔐 SSL Certificate:"
if openssl s_client -connect kulturhaus-bortfeld.de:443 -servername kulturhaus-bortfeld.de </dev/null 2>/dev/null | openssl x509 -noout -dates 2>/dev/null; then
    CERT_EXPIRY=$(echo | openssl s_client -connect kulturhaus-bortfeld.de:443 -servername kulturhaus-bortfeld.de 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
    echo -e "✅ ${GREEN}SSL Certificate${NC} - Valid until $CERT_EXPIRY"
else
    echo -e "❌ ${RED}SSL Certificate${NC} - Check failed"
fi
echo ""

# Check log file sizes
echo "📄 Log Files:"
ODOO_LOG_SIZE=$(du -h /var/log/odoo/odoo18.log 2>/dev/null | cut -f1 || echo "N/A")
NGINX_ACCESS_SIZE=$(du -h /var/log/nginx/kulturhaus-access.log 2>/dev/null | cut -f1 || echo "N/A")
echo -e "📊 ${GREEN}Odoo log size${NC} - $ODOO_LOG_SIZE"
echo -e "📊 ${GREEN}Nginx access log size${NC} - $NGINX_ACCESS_SIZE"
echo ""

# Final summary
echo "==============================================="
echo "Health check completed at $(date)"
echo "==============================================="