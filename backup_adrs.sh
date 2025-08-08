#!/bin/bash
# Local ADR Backup Script
# Protects important Architecture Decision Records locally

BACKUP_DIR="$HOME/.zen_mcp_adrs_backup"
SOURCE_DIR="$(pwd)/tools/tmp"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

echo "🔒 Backing up ADR files locally..."

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Create timestamped backup
BACKUP_PATH="$BACKUP_DIR/adrs_backup_$TIMESTAMP"
mkdir -p "$BACKUP_PATH"

# Copy all ADR files
if [ -d "$SOURCE_DIR" ]; then
    cp -r "$SOURCE_DIR"/* "$BACKUP_PATH/" 2>/dev/null
    echo "✅ ADR files backed up to: $BACKUP_PATH"
    
    # Also copy documentation
    if [ -f "docs/local-customizations.md" ]; then
        cp "docs/local-customizations.md" "$BACKUP_PATH/"
        echo "✅ Documentation backed up"
    fi
    
    # Keep only last 10 backups
    cd "$BACKUP_DIR"
    ls -1t | grep "adrs_backup_" | tail -n +11 | xargs -r rm -rf
    
    echo "📊 Current backups:"
    ls -1t | grep "adrs_backup_" | head -5
else
    echo "❌ ADR directory not found: $SOURCE_DIR"
    exit 1
fi

echo ""
echo "💾 Backup location: $BACKUP_DIR"
echo "🔍 To restore: cp -r $BACKUP_PATH/* tools/tmp/"