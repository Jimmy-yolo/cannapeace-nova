# Smoke Test — Thai-Chinese Translator (D1)

**Before any live demo:** Run this 5-minute checklist to verify the demo works.

---

## Pre-Demo Checklist

- [ ] Demo URL accessible: `http://[RAILWAY_URL]` or `http://localhost:8000`
- [ ] Page loads without errors
- [ ] "DEMO MODE" warning banner visible

---

## Happy Path Test (3 minutes)

### Test 1: Sample Data Upload
1. Open demo URL in browser
2. Click **"Use Sample Invoice"** button (if available) OR upload `samples/sample_chinese_invoice.jpg`
3. Click **"Translate"**
4. **Expected:** Loading spinner appears
5. **Expected:** After 30-60 seconds, "Download PDF" button appears
6. Click **"Download PDF"**
7. **Expected:** Bilingual PDF downloads
8. Open PDF
9. **Verify:**
   - [ ] Chinese text visible (left side)
   - [ ] Thai text visible (right side)
   - [ ] Key fields highlighted (amount, date, payment terms)
   - [ ] "DEMO MODE" watermark or note visible (if sample data used)

### Test 2: Custom Upload (if API keys connected)
1. Upload a real Chinese invoice image
2. Click **"Translate"**
3. **Expected:** Same flow as Test 1
4. **Verify:** Translation is accurate (spot-check a few lines)

---

## Error Cases (1 minute)

### Test 3: No File Selected
1. Click **"Translate"** without uploading a file
2. **Expected:** Error message: "Please select a file" or similar

### Test 4: Non-Image File
1. Upload a `.txt` or `.pdf` file
2. **Expected:** Either accepts it (if OCR supports) OR shows error "Unsupported file type"

---

## Mode Verification (1 minute)

### Test 5: Check DEMO vs LIVE Mode
1. Check `/health` endpoint: `http://[URL]/health`
2. **Expected JSON:**
   ```json
   {
     "status": "ok",
     "mode": "DEMO" or "LIVE",
     "google_vision": "configured" or "demo",
     "openai": "configured" or "demo"
   }
   ```
3. **Verify:** Mode matches expectation (DEMO if no API keys, LIVE if keys configured)

---

## Pass/Fail Criteria

**PASS if:**
- [ ] Sample data upload works end-to-end
- [ ] PDF downloads successfully
- [ ] Bilingual output visible
- [ ] DEMO MODE warning shown when using sample data
- [ ] `/health` endpoint returns correct mode

**FAIL if:**
- [ ] Page doesn't load (500 error, blank page)
- [ ] Upload button doesn't work
- [ ] PDF doesn't download
- [ ] PDF is empty or corrupted
- [ ] No DEMO MODE warning when in demo mode

---

## Troubleshooting

**Issue:** Page loads but upload doesn't work
- **Check:** Console errors (F12 → Console tab)
- **Fix:** Verify FastAPI is running, check CORS settings

**Issue:** PDF downloads but is empty
- **Check:** Backend logs for OCR/translation errors
- **Fix:** Verify sample data paths, check OpenAI API quota

**Issue:** "DEMO MODE" not showing
- **Check:** UI code for warning banner
- **Fix:** Add banner per N4 directive

---

**Smoke test complete. Demo ready for live presentation.**
