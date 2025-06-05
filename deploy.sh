#!/bin/bash

# Snowflake Summit 2025 - Deployment Script
# Automatically commits changes and deploys to GitHub Pages

set -e  # Exit on any error

echo "🚀 Deploying Snowflake Summit 2025 Session Browser..."

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if there are any changes to commit
if git diff --quiet && git diff --staged --quiet; then
    echo "ℹ️  No changes to deploy"
    exit 0
fi

# Get commit message from user or use default
if [ -z "$1" ]; then
    echo "Enter commit message (or press Enter for default):"
    read -r COMMIT_MSG
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update session browser $(date '+%Y-%m-%d %H:%M')"
    fi
else
    COMMIT_MSG="$1"
fi

echo "📝 Commit message: $COMMIT_MSG"

# Add all changes
echo "📋 Adding changes..."
git add .

# Commit changes
echo "💾 Committing changes..."
git commit -m "$COMMIT_MSG"

# Push to GitHub
echo "⬆️  Pushing to GitHub..."
git push

# Check deployment status
echo "🔍 Checking deployment status..."
sleep 3

# Get the latest run ID
RUN_ID=$(gh run list --limit 1 --json databaseId --jq '.[0].databaseId')

if [ -n "$RUN_ID" ]; then
    echo "📊 Deployment started (Run ID: $RUN_ID)"
    echo "🌐 Your site will be updated at: https://pauladam.github.io/snowflake-summit-2025/"
    echo "⏱️  Usually takes 1-2 minutes to deploy"
    echo ""
    echo "To watch deployment progress, run:"
    echo "   gh run watch $RUN_ID"
else
    echo "⚠️  Could not get deployment status, but push was successful"
    echo "🌐 Check your site in a few minutes: https://pauladam.github.io/snowflake-summit-2025/"
fi

echo "✅ Deployment initiated successfully!"