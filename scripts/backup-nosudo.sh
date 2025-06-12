#!/bin/bash

# Kulturhaus Bortfeld - No-Sudo Backup Script
# Usage: ./scripts/backup-nosudo.sh [daily|weekly|manual]
# Note: This version works without sudo but has limited functionality

BACKUP_TYPE=${1:-manual}
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$HOME/backups/kulturhaus"
LOG_FILE="$HOME/backups/kulturhaus_backup.log"

# Create backup directory if it doesn't exist
mkdir -p $BACKUP_DIR
mkdir -p $(dirname $LOG_FILE)

echo "🔄 Starting Kulturhaus Bortfeld backup (no-sudo) - Type: $BACKUP_TYPE"
echo "Date: $(date)" | tee -a $LOG_FILE

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a $LOG_FILE
}

# Database backup (if pg_dump is accessible)
log_message "Attempting database backup..."
DB_BACKUP_FILE="$BACKUP_DIR/kulturhive_${BACKUP_TYPE}_${DATE}.sql"

if command -v pg_dump > /dev/null 2>&1; then
    if pg_dump -h localhost -U odoo18 kulturhive > $DB_BACKUP_FILE 2>/dev/null; then
        log_message "✅ Database backup completed: $DB_BACKUP_FILE"
        DB_SIZE=$(du -h $DB_BACKUP_FILE | cut -f1)
        log_message "Database backup size: $DB_SIZE"
        
        # Compress database backup
        if gzip $DB_BACKUP_FILE; then
            log_message "✅ Database backup compressed: ${DB_BACKUP_FILE}.gz"
        fi
    else
        log_message "⚠️ Database backup failed (permissions or connection issue)"
        rm -f $DB_BACKUP_FILE 2>/dev/null
    fi
else
    log_message "⚠️ pg_dump not available for current user"
fi

# Configuration backup (accessible files only)
log_message "Starting accessible configuration backup..."
CONFIG_BACKUP="$BACKUP_DIR/config_${BACKUP_TYPE}_${DATE}.tar.gz"
CONFIG_FILES=""

# Check which config files are readable
if [ -r /etc/odoo18.conf ]; then
    CONFIG_FILES="$CONFIG_FILES /etc/odoo18.conf"
fi

if [ -r /etc/nginx/sites-available/kulturhaus-bortfeld.conf ]; then
    CONFIG_FILES="$CONFIG_FILES /etc/nginx/sites-available/kulturhaus-bortfeld.conf"
fi

if [ -r /etc/fail2ban/jail.local ]; then
    CONFIG_FILES="$CONFIG_FILES /etc/fail2ban/jail.local"
fi

if [ -n "$CONFIG_FILES" ]; then
    if tar -czf $CONFIG_BACKUP $CONFIG_FILES 2>/dev/null; then
        log_message "✅ Configuration backup completed: $CONFIG_BACKUP"
        CONFIG_SIZE=$(du -h $CONFIG_BACKUP | cut -f1)
        log_message "Configuration backup size: $CONFIG_SIZE"
    else
        log_message "⚠️ Configuration backup failed"
    fi
else
    log_message "⚠️ No readable configuration files found"
fi

# GitHub repository backup (documentation)
log_message "Backing up project documentation..."
DOCS_BACKUP="$BACKUP_DIR/docs_${BACKUP_TYPE}_${DATE}.tar.gz"

if [ -d "$HOME/kulturhaus-docs" ]; then
    if tar -czf $DOCS_BACKUP -C $HOME kulturhaus-docs/ 2>/dev/null; then
        log_message "✅ Documentation backup completed: $DOCS_BACKUP"
        DOCS_SIZE=$(du -h $DOCS_BACKUP | cut -f1)
        log_message "Documentation backup size: $DOCS_SIZE"
    else
        log_message "⚠️ Documentation backup failed"
    fi
else
    log_message "ℹ️ Documentation directory not found at $HOME/kulturhaus-docs"
fi

# System information backup
log_message "Collecting system information..."
SYSINFO_FILE="$BACKUP_DIR/sysinfo_${BACKUP_TYPE}_${DATE}.txt"

{
    echo "=== Kulturhaus Bortfeld System Information ==="
    echo "Date: $(date)"
    echo "Hostname: $(hostname)"
    echo "Uptime: $(uptime)"
    echo ""
    echo "=== System Resources ==="
    free -h
    echo ""
    df -h
    echo ""
    echo "=== Network Interfaces ==="
    ip addr show 2>/dev/null || ifconfig 2>/dev/null
    echo ""
    echo "=== Running Services ==="
    systemctl list-units --type=service --state=running | grep -E "(odoo|nginx|postgresql|ssh|fail2ban)" 2>/dev/null
    echo ""
    echo "=== Process List ==="
    ps aux | grep -E "(odoo|nginx|postgres)" | grep -v grep
    echo ""
    echo "=== Disk Usage Details ==="
    du -sh /var/log/* 2>/dev/null | head -10 || echo "Log directory not accessible"
} > $SYSINFO_FILE

log_message "✅ System information collected: $SYSINFO_FILE"

# Cleanup old backups (keep last 7 daily, 4 weekly)
log_message "Cleaning up old backups..."

case $BACKUP_TYPE in
    "daily")
        # Keep last 7 daily backups
        find $BACKUP_DIR -name "*daily*" -type f -mtime +7 -delete 2>/dev/null
        log_message "Cleaned up daily backups older than 7 days"
        ;;
    "weekly")
        # Keep last 4 weekly backups  
        find $BACKUP_DIR -name "*weekly*" -type f -mtime +28 -delete 2>/dev/null
        log_message "Cleaned up weekly backups older than 4 weeks"
        ;;
esac

# Generate backup report
log_message "Generating backup report..."
TOTAL_SIZE=$(du -sh $BACKUP_DIR | cut -f1)
BACKUP_COUNT=$(ls -1 $BACKUP_DIR/*.gz $BACKUP_DIR/*.txt 2>/dev/null | wc -l)

echo ""
echo "📊 Backup Summary (No-Sudo Version)"
echo "===================================="
echo "Backup type: $BACKUP_TYPE"
echo "Date: $(date)"
echo "Backup location: $BACKUP_DIR"
echo "Total backup directory size: $TOTAL_SIZE"
echo "Number of backup files: $BACKUP_COUNT"
echo ""

# List recent backups
echo "📁 Recent backups:"
ls -lh $BACKUP_DIR/*${DATE}* 2>/dev/null || echo "No backups created today"
echo ""

log_message "✅ Backup process completed successfully (no-sudo version)"
echo "🔄 Backup completed! Check log: $LOG_FILE"
echo ""
echo "💡 Note: For full backups with root access, run backup.sh with sudo on the server"