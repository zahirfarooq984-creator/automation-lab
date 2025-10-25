#!/bin/bash
# ======================================================
# removeproj.sh – Safely remove a Python project folder (with relative-path backup)
# Usage: ./removeproj.sh [project_name]
# ======================================================

BASE_DIR=~/automation-lab
BACKUP_DIR=$BASE_DIR/_backups

# Ask for project name if not provided
if [ -z "$1" ]; then
  read -p "Enter the project folder name to remove (inside python/): " PROJECT
else
  PROJECT=$1
fi

PROJECT_DIR=$BASE_DIR/python/$PROJECT

# Check if folder exists
if [ ! -d "$PROJECT_DIR" ]; then
  echo "❌ Folder '$PROJECT_DIR' does not exist."
  exit 1
fi

# Confirm deletion
read -p "⚠️  Are you sure you want to delete '$PROJECT_DIR'? (y/n): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
  echo "❎ Deletion cancelled."
  exit 0
fi

# Ensure backup directory exists
mkdir -p "$BACKUP_DIR"

# Create a timestamped backup before deletion
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/${PROJECT}_backup_${TIMESTAMP}.zip"

echo "📦 Creating backup: $BACKUP_FILE"

# Backup using relative paths only
cd "$BASE_DIR/python"
zip -r "$BACKUP_FILE" "$PROJECT" > /dev/null

if [ $? -eq 0 ]; then
  echo "✅ Backup successful."
else
  echo "❌ Backup failed. Aborting deletion."
  exit 1
fi

# Remove the folder
rm -rf "$PROJECT_DIR"
echo "🗑️  Removed folder: $PROJECT_DIR"

# Commit and push the change to GitHub
cd $BASE_DIR
git add -u
git commit -m "Removed project folder '$PROJECT' (backup created: ${PROJECT}_backup_${TIMESTAMP}.zip)"
git push

echo "✅ Folder '$PROJECT' removed and change pushed to GitHub."
echo "💾 Backup saved at: $BACKUP_FILE"
