# D2 Railway Deployment - 5 Minute Manual Guide

**Status:** Anthropic migration complete, ready to deploy

---

## Method 1: GitHub Integration (Recommended - 5 minutes)

### Step 1: Create Railway Project
1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select `Jimmy-yolo/cannapeace-nova`
4. Root directory: `demos/restaurant-line-to-excel`

### Step 2: Configure Environment
Add this single environment variable:
```
ANTHROPIC_API_KEY=<your_anthropic_api_key_here>
```
(Jimmy has the key - see session notes)

### Step 3: Deploy
- Railway auto-detects `railway.json` config
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn app:app --host 0.0.0.0 --port $PORT`
- Click "Deploy"

### Step 4: Verify
1. Wait 2-3 minutes for deployment
2. Open the public URL Railway provides
3. You should see the demo homepage with "DEMO MODE" banner
4. Run smoke test: `demos/restaurant-line-to-excel/smoke_test.md`

---

## Method 2: Railway CLI (Alternative)

### If you prefer CLI:
```bash
cd /Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel

# Link to workspace (interactive - select "jimmy-yolo's Projects")
railway link

# Set environment variable
railway variables set ANTHROPIC_API_KEY="<your_anthropic_api_key_here>"

# Deploy
railway up
```

---

## Post-Deployment

### Test Checklist (from smoke_test.md):
1. Open deployed URL
2. Click first sample order
3. Click "Parse Order"
4. Verify JSON result appears
5. Check `/health` endpoint shows `"mode": "LIVE"`

### Optional: Add Google Sheets (for live order tracking)
If you want D2 to actually append orders to a Google Sheet:
1. Create Google Cloud service account
2. Download credentials JSON
3. Add to Railway: `GOOGLE_APPLICATION_CREDENTIALS` (paste JSON as string)
4. Add to Railway: `GOOGLE_SHEET_ID` (your sheet ID)

### Optional: Add LINE Bot (for webhook)
If you want customers to send orders via LINE:
1. Create LINE bot (https://developers.line.biz/)
2. Add to Railway:
   - `LINE_CHANNEL_SECRET`
   - `LINE_CHANNEL_ACCESS_TOKEN`
3. Set LINE webhook URL to `https://[your-railway-url]/webhook`

---

## Pricing (Approved by Jimmy 2026-07-08)

Use these directive-compliant rates when selling:

**Monthly Subscription:**
- 1,500-3,000 THB/month (unlimited orders)

**Setup Fee:**
- 5,000-10,000 THB one-time

---

## Status: READY TO DEPLOY (Anthropic migration complete ✅)
