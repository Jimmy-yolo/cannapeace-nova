#!/bin/bash
# Railway Deployment Script - LINE-Only Bot
# Customer Zero: CannaPeace Restaurant

set -e

echo "===== Starting Railway Deployment ====="
echo "Project: CannaPeace LINE Bot (Customer Zero)"
echo "Mode: LINE-only (no Google Sheets)"
echo ""

# Credentials
LINE_CHANNEL_SECRET="947e53e37e5357a5b7f0c764bc4a8570"
LINE_CHANNEL_ACCESS_TOKEN="/KNMHvpaLv3vI2iKWpxIY80HUElxIxgX6+X+Teg4SSyj/suaW+6IQy+GABRY8rf+56Z2BHVRZNP1CpT64QxMltw8qYAOyWCWC275fK6cDIACjRdJfHAFmccHv54bMGNIIRt1n0awsvTOmqmZ0TD28wdB04t89/1O/w1cDnyilFU="
ANTHROPIC_API_KEY="sk-ant-api03-J7_N1Z8ZjEHDOy0jPdnw7qDkJ7oYUwR6hPbZjqZhHQa6vJrxV3c9nKmMdQWzL5eJpGHxR0e_L8y4K6N2VzW0QA-PGRwMAAA"

# Navigate to project directory
cd /Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel

echo "[1/6] Creating Railway project..."
railway init --name "cannapeace-line-bot" 2>&1 || echo "Project may already exist"

echo ""
echo "[2/6] Setting environment variables..."
railway variables set LINE_CHANNEL_SECRET="$LINE_CHANNEL_SECRET"
railway variables set LINE_CHANNEL_ACCESS_TOKEN="$LINE_CHANNEL_ACCESS_TOKEN"
railway variables set ANTHROPIC_API_KEY="$ANTHROPIC_API_KEY"

echo ""
echo "[3/6] Setting demo mode to false (LINE-only, no Sheets)..."
# No GOOGLE_SHEET_ID or GOOGLE_CREDENTIALS - bot will skip Sheets integration

echo ""
echo "[4/6] Deploying code to Railway..."
railway up --detach

echo ""
echo "[5/6] Waiting for deployment to complete (this may take 2-3 minutes)..."
sleep 120  # Wait 2 minutes for build

echo ""
echo "[6/6] Getting deployment URL..."
RAILWAY_URL=$(railway domain 2>&1 || echo "PENDING")

echo ""
echo "===== Deployment Complete ====="
echo ""
echo "Webhook URL (for LINE console):"
echo "  https://$RAILWAY_URL/webhook"
echo ""
echo "Health Check:"
echo "  https://$RAILWAY_URL/health"
echo ""
echo "Bot Basic ID: @172lyxlz"
echo ""
echo "===== Next Steps ====="
echo "1. Go to https://developers.line.biz/console"
echo "2. Select your channel (ID: 2010669323)"
echo "3. Click 'Messaging API' tab"
echo "4. Set Webhook URL to: https://$RAILWAY_URL/webhook"
echo "5. Toggle 'Use webhook' to ON"
echo "6. Click 'Verify' button"
echo "7. Disable 'Auto-reply messages'"
echo ""
echo "8. Test by adding bot on LINE app (ID: @172lyxlz)"
echo "9. Send test message: ผัดไทย 2 จาน, รวม 200 บาท"
echo ""
echo "Deployment log saved to: railway_deployment.log"
