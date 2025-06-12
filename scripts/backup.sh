#!/bin/bash

# Kulturhaus Bortfeld - Backup Script
# Usage: ./scripts/backup.sh [daily|weekly|manual]

BACKUP_TYPE=${1:-manual}
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="/backup/kulturhaus"
LOG_FILE="/var/log/backup/kulturhaus_backup.log"

# Create backup directory if it doesn't exist
sudo mkdir -p $BACKUP_DIR
sudo mkdir -p /var/log/backup/

echo "🔄 Starting Kulturhaus Bortfeld backup - Type: $BACKUP_TYPE"
echo "Date: $(date)" | sudo tee -a $LOG_FILE

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | sudo tee -a $LOG_FILE
}

# Database backup
log_message "Starting database backup..."
DB_BACKUP_FILE="$BACKUP_DIR/kulturhive_${BACKUP_TYPE}_${DATE}.sql"

if sudo -u postgres pg_dump kulturhive > $DB_BACKUP_FILE; then
    log_message "✅ Database backup completed: $DB_BACKUP_FILE"
    DB_SIZE=$(du -h $DB_BACKUP_FILE | cut -f1)
    log_message "Database backup size: $DB_SIZE"
else
    log_message "❌ Database backup failed"
    exit 1
fi

# Compress database backup
log_message "Compressing database backup..."
if gzip $DB_BACKUP_FILE; then
    log_message "✅ Database backup compressed: ${DB_BACKUP_FILE}.gz"
else
    log_message "⚠️ Database compression failed, but backup exists"
fi

# Odoo filestore backup
log_message "Starting Odoo filestore backup..."
FILESTORE_BACKUP="$BACKUP_DIR/odoo_filestore_${BACKUP_TYPE}_${DATE}.tar.gz"

if sudo tar -czf $FILESTORE_BACKUP -C /opt/odoo18 filestore/ 2>/dev/null; then
    log_message "✅ Odoo filestore backup completed: $FILESTORE_BACKUP"
    FILESTORE_SIZE=$(du -h $FILESTORE_BACKUP | cut -f1)
    log_message "Filestore backup size: $FILESTORE_SIZE"
else
    log_message "⚠️ Odoo filestore backup failed or no filestore found"
fi

# Configuration backup
log_message "Starting configuration backup..."
CONFIG_BACKUP="$BACKUP_DIR/config_${BACKUP_TYPE}_${DATE}.tar.gz"

sudo tar -czf $CONFIG_BACKUP \
    /etc/odoo18.conf \
    /etc/nginx/sites-available/kulturhaus-bortfeld.conf \
    /etc/fail2ban/jail.local \
    2>/dev/null

if [ $? -eq 0 ]; then
    log_message "✅ Configuration backup completed: $CONFIG_BACKUP"
else
    log_message "⚠️ Some configuration files may be missing"
fi

# SSL certificates backup (if accessible)
log_message "Checking SSL certificates..."
if sudo test -d /etc/letsencrypt/live/kulturhaus-bortfeld.de/; then
    SSL_BACKUP="$BACKUP_DIR/ssl_${BACKUP_TYPE}_${DATE}.tar.gz"
    if sudo tar -czf $SSL_BACKUP /etc/letsencrypt/live/kulturhaus-bortfeld.de/ 2>/dev/null; then
        log_message "✅ SSL certificates backup completed: $SSL_BACKUP"
    else
        log_message "⚠️ SSL certificates backup failed"
    fi
else
    log_message "ℹ️ SSL certificates directory not accessible"
fi

# Cleanup old backups (keep last 7 daily, 4 weekly)
log_message "Cleaning up old backups..."

case $BACKUP_TYPE in
    "daily")
        # Keep last 7 daily backups
        sudo find $BACKUP_DIR -name "*daily*" -type f -mtime +7 -delete 2>/dev/null
        log_message "Cleaned up daily backups older than 7 days"
        ;;
    "weekly")
        # Keep last 4 weekly backups  
        sudo find $BACKUP_DIR -name "*weekly*" -type f -mtime +28 -delete 2>/dev/null
        log_message "Cleaned up weekly backups older than 4 weeks"
        ;;
esac

# Generate backup report
log_message "Generating backup report..."
TOTAL_SIZE=$(sudo du -sh $BACKUP_DIR | cut -f1)
BACKUP_COUNT=$(sudo ls -1 $BACKUP_DIR/*.gz 2>/dev/null | wc -l)

echo ""
echo "📊 Backup Summary"
echo "=================="
echo "Backup type: $BACKUP_TYPE"
echo "Date: $(date)"
echo "Total backup directory size: $TOTAL_SIZE"
echo "Number of backup files: $BACKUP_COUNT"
echo ""

# List recent backups
echo "📁 Recent backups:"
sudo ls -lh $BACKUP_DIR/*${DATE}* 2>/dev/null || echo "No backups created today"
echo ""

log_message "✅ Backup process completed successfully"
echo "🔄 Backup completed! Check log: $LOG_FILE"