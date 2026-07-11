# DEMO DAY RUNBOOK — CannaPeace NOVA Demos

**Purpose:** Complete local demo instructions for in-person pitches
**Audience:** Jimmy (must work zero-help)
**Status:** LOCAL FALLBACK READY (Railway deployment optional)

---

## Pre-Demo Setup (15 minutes, ONE TIME)

### System Requirements
- macOS (tested on Darwin 25.5.0)
- Python 3.13+ installed
- Terminal access
- No API keys required for DEMO MODE

### Directory Structure
```
/Users/jimmy/repos/cannapeace-nova/demos/
├── thai-chinese-translator/     # Demo 1 (D1)
└── restaurant-line-to-excel/     # Demo 2 (D2)
```

---

## DEMO 1: Thai-Chinese Document Translator

### Quick Start (< 5 minutes)

```bash
# Navigate to demo directory
cd /Users/jimmy/repos/cannapeace-nova/demos/thai-chinese-translator

# Create virtual environment (first time only)
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies (first time only)
pip install -r requirements.txt

# Start server
uvicorn app:app --port 8000 --reload
```

### Expected Output
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Open Demo in Browser
1. Open: http://localhost:8000
2. Verify "DEMO MODE" banner is visible (yellow/orange warning at top)
3. Click "Use Sample Invoice" or upload `samples/sample_chinese_invoice.jpg`
4. Click "Translate"
5. After 30-60 seconds, download bilingual PDF

### Smoke Test (3 minutes)
```bash
# In another terminal, run health check
curl http://localhost:8000/health

# Expected response:
# {"status":"ok","mode":"DEMO","anthropic":"configured"}
```

### Troubleshooting

**Problem:** `ModuleNotFoundError: No module named 'fastapi'`
**Fix:** Virtual environment not activated. Run `source venv/bin/activate`

**Problem:** Port 8000 already in use
**Fix:** Use different port: `uvicorn app:app --port 8001`

**Problem:** Page loads but upload doesn't work
**Fix:** Check browser console (F12 → Console) for CORS errors

### Stop Demo
Press `CTRL+C` in terminal where uvicorn is running

---

## DEMO 2: Restaurant LINE-to-Excel Bridge

### Quick Start (< 5 minutes)

```bash
# Navigate to demo directory
cd /Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel

# Virtual environment already exists (check with ls -la)
# If not: python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies (first time only)
pip install -r requirements.txt

# Start server
uvicorn app:app --port 8001 --reload
```

### Expected Output
```
INFO:     Uvicorn running on http://127.0.0.1:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
```

### Open Demo in Browser
1. Open: http://localhost:8001
2. Verify "DEMO MODE" banner visible
3. Click "Send Test Order" to simulate LINE message
4. See order appear in sample Google Sheet or local export
5. Check daily summary feature

### Smoke Test (2 minutes)
```bash
# Health check
curl http://localhost:8001/health

# Test webhook endpoint (simulates LINE message)
curl -X POST http://localhost:8001/webhook \
  -H "Content-Type: application/json" \
  -d '{
    "events": [{
      "type": "message",
      "message": {
        "type": "text",
        "text": "ข้าวผัดกุ้ง 2 จาน, น้ำมะนาว 1 แก้ว"
      }
    }]
  }'
```

### Troubleshooting

**Problem:** Google Sheets API error
**Fix:** Demo mode doesn't need real Google Sheets. Orders saved to local JSON file in `outputs/`

**Problem:** LINE SDK errors
**Fix:** Normal in demo mode. Webhook receives test data, doesn't connect to real LINE

### Stop Demo
Press `CTRL+C` in terminal

---

## Running Both Demos Simultaneously

```bash
# Terminal 1: Thai-Chinese Translator
cd /Users/jimmy/repos/cannapeace-nova/demos/thai-chinese-translator
source venv/bin/activate
uvicorn app:app --port 8000

# Terminal 2: Restaurant Bridge
cd /Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel
source venv/bin/activate
uvicorn app:app --port 8001
```

**Demo URLs:**
- Thai-Chinese: http://localhost:8000
- Restaurant: http://localhost:8001

---

## Reset to Clean State (Between Demos)

### Demo 1 (Thai-Chinese)
```bash
cd /Users/jimmy/repos/cannapeace-nova/demos/thai-chinese-translator
rm -rf uploads/* outputs/*
# Restart server to clear in-memory state
```

### Demo 2 (Restaurant)
```bash
cd /Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel
rm -rf outputs/*.json
# Restart server
```

---

## Recovery Steps (If Demo Dies Mid-Pitch)

### Demo Crashes or Freezes
1. Press `CTRL+C` in terminal (kills server)
2. Wait 2 seconds
3. Press `↑` (up arrow) to recall last command
4. Press `Enter` to restart
5. Refresh browser (Cmd+R)
6. Total recovery time: <10 seconds

### Browser Shows Error
1. Open browser DevTools (F12 or Cmd+Option+I)
2. Go to Console tab
3. If CORS error: Restart server
4. If network error: Check server is running
5. If 404 error: Check URL is correct (http://localhost:8000 or :8001)

### Complete System Reset (Worst Case)
```bash
# Kill all Python processes
pkill -f uvicorn

# Wait 5 seconds
sleep 5

# Restart both demos (see "Running Both Demos Simultaneously" above)
```

---

## Pre-Pitch Checklist (5 Minutes Before Demo)

- [ ] Both terminals open and ready
- [ ] Virtual environments activated (see `(venv)` prefix in terminal)
- [ ] Servers started (both on ports 8000 and 8001)
- [ ] Browser tabs open to both demos
- [ ] Health checks passing: `curl http://localhost:8000/health && curl http://localhost:8001/health`
- [ ] DEMO MODE banners visible on both pages
- [ ] Sample data loaded (thai-chinese: `samples/` dir exists, restaurant: `sample_orders.json` exists)
- [ ] Outputs directories clean (or cleared)
- [ ] Laptop on power (not battery)
- [ ] WiFi connected (for any API calls, though demos work offline in DEMO MODE)

---

## Pitch Script Integration

### Demo 1 Flow (3 minutes)
1. **Show problem:** "Chinese suppliers send invoices in Chinese. Staff can't read them."
2. **Show solution:** Upload sample invoice → Click translate
3. **While waiting (30-60s):** Talk about key fields, bilingual layout, cost savings
4. **Show result:** Download PDF, show highlighted amounts/dates
5. **Price anchor:** "300-800 baht manual translation vs 50-100 baht automated"

### Demo 2 Flow (2 minutes)
1. **Show problem:** "Restaurants get 20-50 LINE orders daily. Staff re-type into Excel."
2. **Show solution:** Send test order via demo button
3. **Show result:** Order appears in sheet, parsed correctly
4. **Daily summary:** Show aggregated sales/top items
5. **Price anchor:** "499-999 baht/month vs 2-4 hours daily labor"

---

## Backup Plan (If Laptop Fails Completely)

1. **Phone demo:** Both demos should work on phone browser (mobile-responsive)
2. **Video fallback:** Record 2-minute demo videos beforehand, show on phone
3. **Slide deck:** Static screenshots of key demo steps
4. **Live coding:** Show `app.py` source code, explain logic (if technical audience)

---

## DEMO MODE vs LIVE MODE

**DEMO MODE (No API Keys):**
- Uses sample/mock data
- Works offline
- Instant responses (no API latency)
- "DEMO MODE" banner visible
- Safe to show in pitches (no real API costs)

**LIVE MODE (API Keys Configured):**
- Real OCR and translation (Google Vision + Claude API)
- Real LINE webhook integration
- Real Google Sheets updates
- Slower (API latency 30-60 seconds)
- Costs per API call
- Only use if client insists on "real data" test

**How to Switch:**
- DEMO MODE: No `.env` file or empty API keys
- LIVE MODE: Create `.env` file with real keys (see `.env.example`)

---

## Post-Demo Cleanup

```bash
# Deactivate virtual environments
deactivate  # Run in each terminal

# Stop servers (if not already stopped)
pkill -f uvicorn

# Optional: Clear all demo data
cd /Users/jimmy/repos/cannapeace-nova/demos
rm -rf thai-chinese-translator/uploads/* thai-chinese-translator/outputs/*
rm -rf restaurant-line-to-excel/outputs/*.json
```

---

## Quick Reference Commands

```bash
# Start Demo 1 (Thai-Chinese)
cd ~/repos/cannapeace-nova/demos/thai-chinese-translator && source venv/bin/activate && uvicorn app:app --port 8000

# Start Demo 2 (Restaurant)
cd ~/repos/cannapeace-nova/demos/restaurant-line-to-excel && source venv/bin/activate && uvicorn app:app --port 8001

# Health checks
curl http://localhost:8000/health && curl http://localhost:8001/health

# Stop all demos
pkill -f uvicorn
```

---

**Last Updated:** 2026-07-08
**Tested On:** macOS Darwin 25.5.0, Python 3.13.3
**Maintainer:** Howard (via Claude Code)
**Status:** READY FOR IN-PERSON DEMO

**🚨 IMPORTANT:** This runbook is designed for LOCAL DEMOS ONLY. Railway deployment is optional and NOT required for in-person pitches.
