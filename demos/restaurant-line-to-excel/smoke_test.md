# Smoke Test — Restaurant LINE-to-Excel (D2)

**Before any live demo:** Run this 5-minute checklist to verify the demo works.

---

## Pre-Demo Checklist

- [ ] Demo URL accessible: `http://[RAILWAY_URL]` or `http://localhost:8001`
- [ ] Page loads without errors
- [ ] "DEMO MODE" warning banner visible
- [ ] Sample orders load in sidebar

---

## Happy Path Test (3 minutes)

### Test 1: Sample Order Parsing
1. Open demo URL in browser
2. Click **first sample order** in the left sidebar
3. Verify order text appears in textarea
4. Click **"Parse Order"**
5. **Expected:** Result appears in right panel showing:
   ```json
   {
     "parsed_order": {
       "customer_name": "...",
       "phone": "...",
       "items": [...],
       "total": 350
     },
     "appended_to_sheet": true/false,
     "mode": "DEMO" or "LIVE"
   }
   ```
6. **Verify:**
   - [ ] Customer name extracted correctly
   - [ ] Phone number formatted correctly
   - [ ] Items list accurate
   - [ ] Total amount matches

### Test 2: Multiple Sample Orders
1. Click through **3-5 different sample orders**
2. Parse each one
3. **Verify:** All parse successfully with correct data

### Test 3: Daily Summary
1. Navigate to `/daily-summary` endpoint
2. **Expected JSON:**
   ```json
   {
     "date": "2026-07-08",
     "total_orders": 10,
     "total_revenue": 4850,
     "top_items": [...],
     "summary_message": "📊 สรุปยอดวันนี้...",
     "mode": "DEMO"
   }
   ```
3. **Verify:**
   - [ ] Summary message in Thai
   - [ ] Top 3 items listed
   - [ ] Revenue total shown

---

## Error Cases (1 minute)

### Test 4: Empty Input
1. Clear textarea (no order message)
2. Click **"Parse Order"**
3. **Expected:** Error message or empty result

### Test 5: Invalid Format
1. Type random text: "hello world testing 123"
2. Click **"Parse Order"**
3. **Expected:** Either graceful fallback (Demo Customer) OR error message

---

## Mode Verification (1 minute)

### Test 6: Check DEMO vs LIVE Mode
1. Check `/health` endpoint: `http://[URL]:8001/health`
2. **Expected JSON:**
   ```json
   {
     "status": "ok",
     "mode": "DEMO" or "LIVE",
     "line_webhook": "configured" or "demo",
     "google_sheets": "configured" or "demo"
   }
   ```
3. **Verify:** Mode matches expectation

### Test 7: Samples Endpoint
1. Check `/samples` endpoint
2. **Expected:** JSON with 10 sample orders
3. **Verify:** All 10 samples have `id`, `message`, `expected` fields

---

## Pass/Fail Criteria

**PASS if:**
- [ ] All sample orders parse correctly
- [ ] Daily summary endpoint returns data
- [ ] DEMO MODE warning visible
- [ ] `/health` shows correct mode
- [ ] `/samples` returns 10 orders

**FAIL if:**
- [ ] Page doesn't load
- [ ] Parsing fails on sample orders
- [ ] Daily summary returns error
- [ ] No DEMO MODE warning
- [ ] Sample orders don't load

---

## Live Integration Test (Optional, if APIs connected)

### Test 8: LINE Webhook (Requires LINE bot setup)
1. Send test message to LINE bot
2. **Expected:** Bot replies with parsed order confirmation
3. **Verify:** Google Sheet updated with new row

### Test 9: Google Sheets (Requires credentials)
1. Parse an order
2. Check Google Sheet directly
3. **Verify:** New row appended with correct data

---

## Troubleshooting

**Issue:** Sample orders don't load
- **Check:** `/samples` endpoint, verify `sample_orders.json` exists
- **Fix:** Ensure JSON file in same directory as `app.py`

**Issue:** Parsing returns "Demo Customer" for all orders
- **Check:** `/health` — mode should show "DEMO"
- **Fix:** Expected behavior without OpenAI API key

**Issue:** Daily summary shows error
- **Check:** Backend logs for Google Sheets API errors
- **Fix:** Normal in DEMO mode, should return sample data

**Issue:** "DEMO MODE" banner not showing
- **Check:** HTML source for warning div
- **Fix:** Added per N4 directive, verify deployment

---

**Smoke test complete. Demo ready for live presentation.**
