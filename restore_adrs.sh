#!/bin/bash
# ADR Recovery Script
# Restores ADR files from local backup

BACKUP_DIR="$HOME/.zen_mcp_adrs_backup"
TARGET_DIR="$(pwd)/tools/tmp"

echo "🔄 ADR Recovery Script"
echo ""

# Check if backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
    echo "❌ No backup directory found at: $BACKUP_DIR"
    echo "💡 Run ./backup_adrs.sh first to create backups"
    exit 1
fi

# List available backups
echo "📂 Available backups:"
cd "$BACKUP_DIR"
BACKUPS=($(ls -1t | grep "adrs_backup_"))

if [ ${#BACKUPS[@]} -eq 0 ]; then
    echo "❌ No backups found in: $BACKUP_DIR"
    exit 1
fi

# Show backups with numbers
for i in "${!BACKUPS[@]}"; do
    BACKUP_DATE=$(echo "${BACKUPS[$i]}" | sed 's/adrs_backup_//' | sed 's/_/ /')
    echo "  $((i+1)). ${BACKUPS[$i]} ($(date -d "${BACKUP_DATE//_/:}" 2>/dev/null || echo "${BACKUPS[$i]}"))"
done

echo ""
echo "Select backup to restore (1-${#BACKUPS[@]}), or 'q' to quit:"
read -r choice

if [ "$choice" = "q" ] || [ "$choice" = "Q" ]; then
    echo "🚪 Exiting without restoring"
    exit 0
fi

# Validate choice
if ! [[ "$choice" =~ ^[0-9]+$ ]] || [ "$choice" -lt 1 ] || [ "$choice" -gt ${#BACKUPS[@]} ]; then
    echo "❌ Invalid choice: $choice"
    exit 1
fi

# Get selected backup
SELECTED_BACKUP="${BACKUPS[$((choice-1))]}"
BACKUP_PATH="$BACKUP_DIR/$SELECTED_BACKUP"

echo ""
echo "🔄 Restoring from: $SELECTED_BACKUP"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Copy files back
if [ -d "$BACKUP_PATH" ]; then
    cp -r "$BACKUP_PATH"/* "$TARGET_DIR/" 2>/dev/null
    
    # Also restore documentation if present
    if [ -f "$BACKUP_PATH/local-customizations.md" ]; then
        cp "$BACKUP_PATH/local-customizations.md" "docs/"
        echo "✅ Documentation restored"
    fi
    
    echo "✅ ADR files restored to: $TARGET_DIR"
    echo ""
    echo "📄 Restored files:"
    ls -la "$TARGET_DIR"
else
    echo "❌ Backup directory not found: $BACKUP_PATH"
    exit 1
fi

echo ""
echo "🎉 Recovery complete! Your ADR files are restored."