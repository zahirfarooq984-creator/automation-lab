#!/bin/bash
# ======================================================
# newproj.sh – Create a new Python project in automation-lab
# Usage: ./newproj.sh  (you will be prompted for a name)
# ======================================================

# Ask for a project name if not provided
if [ -z "$1" ]; then
  read -p "Enter your new project name: " PROJECT
else
  PROJECT=$1
fi

BASE_DIR=~/automation-lab
PROJECT_DIR=$BASE_DIR/python/$PROJECT
VENV=~/automation-lab-env/bin/activate

# Ensure base folder exists
mkdir -p $PROJECT_DIR

# Create a Python script named after the project
SCRIPT_FILE="$PROJECT_DIR/${PROJECT}.py"

if [ ! -f "$SCRIPT_FILE" ]; then
  echo "print('Hello from $PROJECT!')" > "$SCRIPT_FILE"
  echo "✅ Created $SCRIPT_FILE"
else
  echo "⚠️  $SCRIPT_FILE already exists"
fi

# Activate virtual environment (if it exists)
if [ -f "$VENV" ]; then
  source $VENV
  echo "💻 Virtual environment activated"
else
  echo "⚠️  Virtual environment not found, skipping..."
fi

# Git add, commit, and push
cd $BASE_DIR
git add python/$PROJECT
git commit -m "Add new project: $PROJECT"
git push

# Ask if user wants to open VS Code
read -p "🧠 Do you want to open VS Code now? (y/n): " OPEN_CODE
if [[ "$OPEN_CODE" =~ ^[Yy]$ ]]; then
  code $BASE_DIR
  echo "🚀 VS Code opened in $BASE_DIR"
else
  echo "👍 Skipped opening VS Code."
fi

echo "✅ Project '$PROJECT' created and pushed to GitHub successfully!"
