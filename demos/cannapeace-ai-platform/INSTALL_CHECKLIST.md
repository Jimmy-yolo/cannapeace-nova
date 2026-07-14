# INSTALL_CHECKLIST — Restaurant LINE-to-Excel Bridge

**Per:** DELIVERY_PLAYBOOK P1b (Customer Zero rehearsal)
**Purpose:** Step-by-step deployment checklist WITH TIMING for real customer installs
**Date:** 2026-07-10

---

## Pre-Deployment (Customer Preparation)

**Timeline:** 2-3 days before deployment

### Customer Must Provide

- [ ] LINE Official Account credentials
  - Channel Secret
  - Channel Access Token
  - How to get: https://developers.line.biz/console
  - **Time estimate:** 10-15 minutes (if account already exists)
  - **FRICTION POINT:** Customer may not have OA account yet → Add 1-2 days

- [ ] Google Sheet ID
  - Sheet must be created and shared with service account email
  - Service account email: `[TO BE PROVIDED DURING SETUP]`
  - **Time estimate:** 5 minutes
  - **FRICTION POINT:** Customer may not understand service account sharing

- [ ] Sample order messages (≥10 real examples)
  - Format: Thai/Chinese/English text messages
  - Include: Customer name, phone, items, quantities, totals
  - **Time estimate:** 15 minutes
  - **FRICTION POINT:** Customer may send screenshots instead of text

- [ ] Complete menu with prices
  - All items in all supported languages
  - **Time estimate:** 20-30 minutes
  - **FRICTION POINT:** Menu may be incomplete or have typos

---

## Step 1: Local Environment Setup

**Timeline:** 15-20 minutes

### 1.1 Clone Repository

```bash
cd /Users/jimmy/repos
git clone https://github.com/Jimmy-yolo/cannapeace-nova.git
cd cannapeace-nova/demos/restaurant-line-to-excel
```

- [ ] Repository cloned
- **Time:** 2 minutes
- **FRICTION:** None (public repo)

### 1.2 Install Dependencies

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

- [ ] Virtual environment created
- [ ] Dependencies installed
- **Time:** 3-5 minutes
- **FRICTION:** May need Python 3.9+ (check `python3 --version`)

### 1.3 Google Cloud Setup (Service Account)

**Required for Google Sheets access**

1. Go to: https://console.cloud.google.com/
2. Create new project: "Restaurant-LINE-Bot-[CustomerName]"
3. Enable Google Sheets API
4. Create Service Account:
   - IAM & Admin → Service Accounts → Create
   - Name: `restaurant-bot-service`
   - Role: None needed
   - Create key (JSON format)
   - Download `credentials.json`

- [ ] GCP project created
- [ ] Sheets API enabled
- [ ] Service account created
- [ ] credentials.json downloaded
- **Time:** 8-10 minutes
- **FRICTION:** Customer unfamiliar with GCP console

**CRITICAL:** Save service account email (format: `restaurant-bot-service@project-id.iam.gserviceaccount.com`)

---

## Step 2: Configuration

**Timeline:** 10-15 minutes

### 2.1 Create Customer Config

```bash
cp customer_config.json.example customer_config.json
nano customer_config.json  # Or use VS Code, etc.
```

**Fill in:**
- `business_name` (Thai/English/Chinese)
- `menu_items` array (complete menu with prices)
- `supported_languages` (e.g., `["thai", "chinese"]`)
- Adjust `parsing_config` if needed (require_phone, require_customer_name)

- [ ] customer_config.json created
- [ ] Business names filled
- [ ] Menu items complete
- [ ] Languages configured
- **Time:** 10-12 minutes
- **FRICTION:** Menu entry tedious, customer may have typos

### 2.2 Set Environment Variables

```bash
export LINE_CHANNEL_SECRET="[FROM_CUSTOMER]"
export LINE_CHANNEL_ACCESS_TOKEN="[FROM_CUSTOMER]"
export GOOGLE_SHEET_ID="[FROM_CUSTOMER]"
export GOOGLE_CREDENTIALS_PATH="$(pwd)/credentials.json"
```

- [ ] LINE credentials set
- [ ] Google credentials set
- [ ] Sheet ID set
- **Time:** 2 minutes
- **FRICTION:** Customer may send wrong credentials (e.g., User ID instead of Channel Secret)

### 2.3 Share Sheet with Service Account

**Customer action required:**

1. Open Google Sheet
2. Click "Share"
3. Add service account email: `restaurant-bot-service@...iam.gserviceaccount.com`
4. Permission: "Editor"
5. Uncheck "Notify people"

- [ ] Sheet shared with service account
- **Time:** 2 minutes
- **FRICTION:** Customer may forget this step → 403 errors

---

## Step 3: Local Testing

**Timeline:** 10-15 minutes

### 3.1 Test Credentials

```bash
python3 << 'EOF'
import os
from google.oauth2 import service_account
from googleapiclient.discovery import build

creds = service_account.Credentials.from_service_account_file(
    os.getenv('GOOGLE_CREDENTIALS_PATH'),
    scopes=['https://www.googleapis.com/auth/spreadsheets']
)
service = build('sheets', 'v4', credentials=creds)
sheet_id = os.getenv('GOOGLE_SHEET_ID')

# Test read
result = service.spreadsheets().values().get(
    spreadsheetId=sheet_id, range='A1:A1'
).execute()
print(f"✅ Google Sheets access OK: {result}")

# Test LINE webhook (basic)
import requests
token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
r = requests.get(
    'https://api.line.me/v2/bot/info',
    headers={'Authorization': f'Bearer {token}'}
)
print(f"✅ LINE bot info: {r.json()}")
EOF
```

- [ ] Google Sheets access verified
- [ ] LINE token verified
- **Time:** 3 minutes
- **FRICTION:** 403 error if sheet not shared correctly

### 3.2 Start Local Server

```bash
uvicorn app:app --port 8001 --reload
```

- [ ] Server started on http://localhost:8001
- [ ] Health check: `curl http://localhost:8001/health` → `{"status":"ok","demo_mode":true}`
- **Time:** 1 minute
- **FRICTION:** Port 8001 may be in use

### 3.3 Test Parse Endpoint

```bash
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"message": "ผัดไทย 2 จาน, ต้มยำกุ้ง 1 ถ้วย, รวม 350 บาท, คุณสมชาย โทร 081-234-5678"}'
```

**Expected:** JSON with parsed order (customer_name, phone, items, total)

- [ ] Parse test successful
- [ ] Items recognized from menu
- [ ] Total extracted correctly
- **Time:** 2-3 minutes
- **FRICTION:** Parser may fail if menu items misspelled

### 3.4 Test Daily Summary

```bash
curl http://localhost:8001/daily-summary
```

- [ ] Summary returned (total_orders, total_revenue, top_items)
- **Time:** 1 minute
- **FRICTION:** None

---

## Step 4: Deploy to Railway

**Timeline:** 20-25 minutes

### 4.1 Install Railway CLI

```bash
# macOS
brew install railway

# Windows
npm i -g @railway/cli

# Linux
curl -fsSL https://railway.app/install.sh | sh
```

- [ ] Railway CLI installed
- [ ] `railway --version` works
- **Time:** 3 minutes
- **FRICTION:** May need npm/brew first

### 4.2 Login and Initialize

```bash
railway login  # Opens browser
railway init
# Project name: restaurant-line-[customername]
# Region: asia-southeast1 (Singapore)
```

- [ ] Railway logged in
- [ ] Project created
- **Time:** 3 minutes
- **FRICTION:** Browser may not open (use `railway login --browserless`)

### 4.3 Add Environment Variables

```bash
railway variables set LINE_CHANNEL_SECRET="[VALUE]"
railway variables set LINE_CHANNEL_ACCESS_TOKEN="[VALUE]"
railway variables set GOOGLE_SHEET_ID="[VALUE]"
```

**For Google credentials (multi-line JSON):**
```bash
railway variables set GOOGLE_CREDENTIALS="$(cat credentials.json | tr -d '\n')"
```

- [ ] All 4 environment variables set
- **Time:** 3 minutes
- **FRICTION:** credentials.json must be valid JSON

### 4.4 Create Procfile

```bash
cat > Procfile <<EOF
web: uvicorn app:app --host 0.0.0.0 --port \$PORT
EOF
```

- [ ] Procfile created
- **Time:** 1 minute
- **FRICTION:** None

### 4.5 Deploy

```bash
railway up
```

**Watch deployment:**
```bash
railway logs
```

- [ ] Code uploaded
- [ ] Build succeeded
- [ ] Service started
- **Time:** 5-8 minutes
- **FRICTION:** Build may fail if requirements.txt wrong

### 4.6 Get Deployment URL

```bash
railway domain  # Or get from Railway dashboard
```

**Example:** `https://restaurant-line-customername-production.up.railway.app`

- [ ] Deployment URL obtained
- [ ] Health check: `curl https://[URL]/health` → `{"status":"ok","demo_mode":false}`
- **Time:** 1 minute
- **FRICTION:** None

---

## Step 5: LINE Webhook Configuration

**Timeline:** 5-10 minutes

### 5.1 Set Webhook URL

1. Go to: https://developers.line.biz/console
2. Select channel
3. Messaging API tab
4. Webhook settings:
   - Webhook URL: `https://[RAILWAY_URL]/webhook`
   - Use webhook: ON
   - Verify: Click "Verify" button
5. Auto-reply messages: OFF
6. Greeting messages: Optional

- [ ] Webhook URL set
- [ ] Webhook verification passed (200 OK)
- [ ] Auto-reply disabled
- **Time:** 5 minutes
- **FRICTION:** Customer may forget to enable webhook

---

## Step 6: End-to-End Test

**Timeline:** 10-15 minutes

### 6.1 Send Test Order via LINE

**Have customer send:**
```
ผัดไทย 2 จาน
ต้มยำกุ้ง 1 ถ้วย
รวม 350 บาท
คุณสมชาย
โทร 081-234-5678
```

- [ ] LINE message sent
- [ ] Bot responds with confirmation
- [ ] Order appears in Google Sheet
- **Time:** 2 minutes
- **FRICTION:** Bot may not respond if webhook wrong

### 6.2 Verify Sheet Append

Check Google Sheet:
- Row added with timestamp, customer name, phone, items, total

- [ ] Data in sheet correct
- [ ] Timestamp correct (Asia/Bangkok timezone)
- **Time:** 1 minute
- **FRICTION:** None

### 6.3 Test Daily Summary

Send LINE message: `/summary` (or configure trigger word)

- [ ] Summary message received
- [ ] Total orders correct
- [ ] Total revenue correct
- **Time:** 2 minutes
- **FRICTION:** Customer may want different trigger word

### 6.4 Test Multiple Languages

Send orders in Thai, Chinese, English (if supported)

- [ ] All languages parsed correctly
- [ ] Menu items matched across languages
- **Time:** 5 minutes
- **FRICTION:** None

---

## Step 7: Handoff to Customer

**Timeline:** 30 minutes

### 7.1 Walkthrough Session

**Screen share with customer:**
1. Show Google Sheet structure
2. Demonstrate sending orders via LINE
3. Show daily summary
4. Explain how to restart if needed

- [ ] Customer understands flow
- [ ] Customer can send test orders
- **Time:** 15 minutes
- **FRICTION:** Customer may need multiple examples

### 7.2 Provide Documentation

Give customer:
- README.md (how to restart, troubleshooting)
- Railway dashboard access
- Support contact (email/LINE)

- [ ] Documentation sent
- [ ] Railway access granted
- **Time:** 5 minutes
- **FRICTION:** None

### 7.3 Schedule Follow-Up

- First check-in: 24 hours
- Second check-in: 3 days
- Final check-in: 1 week

- [ ] Follow-up schedule agreed
- **Time:** 2 minutes
- **FRICTION:** None

---

## Total Time Estimate

| Phase | Estimated Time | Actual Time |
|-------|----------------|-------------|
| Pre-deployment (customer prep) | 2-3 days | |
| Local environment setup | 15-20 min | |
| Configuration | 10-15 min | |
| Local testing | 10-15 min | |
| Railway deployment | 20-25 min | |
| LINE webhook config | 5-10 min | |
| End-to-end test | 10-15 min | |
| Customer handoff | 30 min | |
| **TOTAL (Active Work)** | **1.5-2 hours** | |

---

## Common Issues & Solutions

### Issue 1: "403 Forbidden" on Google Sheets

**Symptom:** App can't write to sheet
**Cause:** Sheet not shared with service account
**Fix:** Share sheet with `[service-account]@...iam.gserviceaccount.com` (Editor permission)

### Issue 2: LINE bot not responding

**Symptom:** Messages sent, no response
**Cause:** Webhook URL incorrect or not enabled
**Fix:**
1. Check webhook URL in LINE console
2. Verify webhook (should return 200 OK)
3. Enable "Use webhook"
4. Disable auto-reply

### Issue 3: Parser not recognizing menu items

**Symptom:** Items not extracted from message
**Cause:** Menu item names don't match customer_config.json
**Fix:** Update customer_config.json menu_items with exact customer wording

### Issue 4: Railway deployment fails

**Symptom:** Build error or service crash
**Cause:** Missing environment variables or wrong Python version
**Fix:**
1. Check all 4 env vars are set: `railway variables`
2. Check logs: `railway logs`
3. Verify requirements.txt has correct versions

---

## Acceptance Test Criteria

**Pass = Customer pays final 50%**

- [ ] 3 consecutive days of real orders
- [ ] ≥90% parse accuracy (9/10 orders parsed correctly)
- [ ] Daily summary delivered on time (within 5 minutes of request)
- [ ] Zero bot downtime during test period
- [ ] Customer can independently restart service if needed

---

## Notes for Next Install

**What worked well:**
- [TO BE FILLED DURING CUSTOMER ZERO]

**What was difficult:**
- [TO BE FILLED]

**Improvements for customer #2:**
- [TO BE FILLED]

**Estimated time for next install:** [ACTUAL TIME FROM THIS INSTALL]
