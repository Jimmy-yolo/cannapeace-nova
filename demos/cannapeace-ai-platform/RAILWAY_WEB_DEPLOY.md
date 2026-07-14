# Railway Web UI Deployment Guide
**Customer Zero: CannaPeace LINE Bot**
**Mode:** LINE-only (no Google Sheets)
**Time:** 10 minutes

---

## Step 1: Create New Project (2 min)

1. Go to: https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Connect GitHub if not already connected
4. Select repository: **`cannapeace-nova`**
5. Select directory: **`demos/restaurant-line-to-excel`**
6. Click **"Deploy Now"**

---

## Step 2: Set Environment Variables (3 min)

1. In Railway dashboard, click on your new project
2. Click **"Variables"** tab
3. Add these 3 variables:

```
LINE_CHANNEL_SECRET=947e53e37e5357a5b7f0c764bc4a8570

LINE_CHANNEL_ACCESS_TOKEN=/KNMHvpaLv3vI2iKWpxIY80HUElxIxgX6+X+Teg4SSyj/suaW+6IQy+GABRY8rf+56Z2BHVRZNP1CpT64QxMltw8qYAOyWCWC275fK6cDIACjRdJfHAFmccHv54bMGNIIRt1n0awsvTOmqmZ0TD28wdB04t89/1O/w1cDnyilFU=

ANTHROPIC_API_KEY=sk-ant-api03-J7_N1Z8ZjEHDOy0jPdnw7qDkJ7oYUwR6hPbZjqZhHQa6vJrxV3c9nKmMdQWzL5eJpGHxR0e_L8y4K6N2VzW0QA-PGRwMAAA
```

4. Click **"Add"** for each one

---

## Step 3: Wait for Deployment (3 min)

1. Go to **"Deployments"** tab
2. Wait for status to show **"SUCCESS"** (green checkmark)
3. If it fails, click on the deployment to see logs

---

## Step 4: Generate Public Domain (1 min)

1. Click **"Settings"** tab
2. Scroll to **"Domains"** section
3. Click **"Generate Domain"**
4. Copy the domain (e.g., `cannapeace-line-bot-production.up.railway.app`)

---

## Step 5: Configure LINE Webhook (2 min)

1. Go to: https://developers.line.biz/console
2. Select channel: **2010669323**
3. Click **"Messaging API"** tab
4. Find **"Webhook URL"** section
5. Enter: `https://[YOUR_RAILWAY_DOMAIN]/webhook`
   - Example: `https://cannapeace-line-bot-production.up.railway.app/webhook`
6. Click **"Update"**
7. Toggle **"Use webhook"** to **ON**
8. Click **"Verify"** button → Should show **"Success"**
9. Toggle **"Auto-reply messages"** to **OFF**

---

## Step 6: Test (2 min)

### Test 1: Health Check
Open in browser: `https://[YOUR_RAILWAY_DOMAIN]/health`

**Expected:**
```json
{
  "status": "ok",
  "demo_mode": false
}
```

### Test 2: Add Bot on LINE App
1. Open LINE app on your phone
2. Tap **"Home"** → **"Add friends"** → **"Search"**
3. Search for: **`@172lyxlz`**
4. Add as friend

### Test 3: Send Test Order
Send this message to the bot:
```
ผัดไทย 2 จาน
ต้มยำกุ้ง 1 ถ้วย
รวม 350 บาท
```

**Expected bot response:**
```
✅ รับออเดอร์แล้วค่ะ!

📝 รายการ: ผัดไทย 2 จาน, ต้มยำกุ้ง 1 ถ้วย
💰 รวม: 350 บาท

✨ ขอบคุณค่ะ - CannaPeace Restaurant
```

---

## Troubleshooting

### Issue: Webhook Verification Fails
**Fix:**
1. Check Railway deployment status is "SUCCESS"
2. Check webhook URL has `/webhook` at the end
3. Try regenerating domain in Railway

### Issue: Bot Doesn't Respond
**Fix:**
1. Check Railway logs: Click deployment → View logs
2. Verify all 3 environment variables are set
3. Ensure "Use webhook" is ON and "Auto-reply" is OFF

### Issue: Bot Responds with Error
**Fix:**
1. Check Railway logs for error details
2. Most likely: ANTHROPIC_API_KEY issue (quota or invalid)

---

## What's Working (LINE-Only Mode)

✅ Receives LINE messages
✅ Parses orders using Claude AI
✅ Responds with confirmation
❌ **NOT** logging to Google Sheets (will add later)

---

## Add Google Sheets Later (Optional)

When ready, add these 2 variables in Railway:
```
GOOGLE_SHEET_ID=1MdkNhpkRwA1BlNv6QDpxTkFimY9z6Rll72sfhmiga9M
GOOGLE_CREDENTIALS=[JSON file content]
```

Then orders will automatically log to the sheet.

---

## Success Checklist

- [ ] Railway deployment shows "SUCCESS"
- [ ] Health check returns `{"status": "ok"}`
- [ ] Webhook verification passes in LINE console
- [ ] Bot added on LINE app (@172lyxlz)
- [ ] Test message gets response from bot
- [ ] Response shows parsed order correctly

---

**Deployment complete!** Bot is now live and responding to LINE messages.

**Next:** Use for 3 days, document any issues in FRICTION_LOG.md
