#!/bin/bash
# ======================================================
# restoreproj.sh – Restore a deleted project from backup
# Works with backups created by removeproj.sh
# Handles both absolute and relative paths in zip
# Usage: ./restoreproj.sh [backup_zip_file]
# ======================================================

BASE_DIR=~/automation-lab
BACKUP_DIR=$BASE_DIR/_backups
RESTORE_DIR=$BASE_DIR/python

# Make sure backup directory exists
if [ ! -d "$BACKUP_DIR" ]; then
  echo "❌ No backup directory found at $BACKUP_DIR"
  exit 1
fi

cd "$BACKUP_DIR"

# If no argument was given, list available backups
if [ -z "$1" ]; then
  echo "📦 Available backups:"
  ls -1 *.zip 2>/dev/null || echo "No backups found!"
  echo
  read -p "Enter the exact name of the backup file to restore: " BACKUP_FILE
else
  BACKUP_FILE=$1
fi

# Check that the file exists
if [ ! -f "$BACKUP_FILE" ]; then
  echo "❌ Backup file '$BACKUP_FILE' not found!"
  exit 1
fi

# Extract project name from the backup filename
PROJECT_NAME=$(echo "$BACKUP_FILE" | sed -E 's/_backup_.*//')

echo "🔄 Restoring project '$PROJECT_NAME' from backup: $BACKUP_FILE"

# Create a temporary directory for extraction
TMP_DIR=$(mktemp -d)
unzip -o "$BACKUP_FILE" -d "$TMP_DIR" > /dev/null

# Determine correct folder inside the temp dir
if [ -d "$TMP_DIR/home/zf/automation-lab/python/$PROJECT_NAME" ]; then
  mv "$TMP_DIR/home/zf/automation-lab/python/$PROJECT_NAME" "$RESTORE_DIR/"
elif [ -d "$TMP_DIR/$PROJECT_NAME" ]; then
  mv "$TMP_DIR/$PROJECT_NAME" "$RESTORE_DIR/"
else
  echo "❌ Could not locate restored folder inside the zip."
  rm -rf "$TMP_DIR"
  exit 1
fi

# Clean up temp directory
rm -rf "$TMP_DIR"

# Commit and push restoration to GitHub
cd "$BASE_DIR"
git add python/$PROJECT_NAME
git commit -m "Restored project '$PROJECT_NAME' from backup $BACKUP_FILE"
git push

echo "✅ Project '$PROJECT_NAME' restored successfully to $RESTORE_DIR/$PROJECT_NAME"
echo "✅ Restoration committed and pushed to GitHub."
