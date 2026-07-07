# D1: Thai-Chinese Document Translator DEMO

**Build Time:** Days 1-2 (2026-07-08 to 2026-07-09)
**Mode:** DEMO (happy path only, sample data)
**Acceptance:** Jimmy runs full flow in <5 min, zero help

---

## Demo Scope (Happy Path Only)

**IN SCOPE:**
- Web upload page (single file)
- 3-5 Chinese invoice samples (realistic or Jimmy-supplied)
- OCR extraction (Chinese text)
- GPT-4 translation (Chinese → Thai)
- Bilingual PDF output (side-by-side layout)
- Key field highlighting (amount, date, payment terms)

**OUT OF SCOPE (not building):**
- Authentication / user accounts
- Billing / payment processing
- Multi-file batch upload
- LINE bot integration
- Correction/learning loops
- Edge case handling (bad images, non-invoices)
- Multi-tenant / database
- Historical translations

---

## Tech Stack (Simplest Possible)

**Backend:**
- Python FastAPI (single file)
- Google Cloud Vision API (Chinese OCR)
- OpenAI GPT-4 API (translation)
- ReportLab (PDF generation)

**Frontend:**
- Single HTML page (no framework)
- Drag & drop file upload
- Display result PDF inline

**Deployment:**
- Railway (single service)
- No database (stateless)

---

## Demo Flow (5 Minutes)

1. Jimmy opens web page
2. Drags Chinese invoice image
3. Clicks "Translate"
4. Waits 30-60 seconds
5. Bilingual PDF appears (download/view)
6. PDF shows:
   - Left side: Original Chinese
   - Right side: Thai translation
   - Key fields highlighted in yellow: จำนวนเงิน (amount), วันที่ (date), เงื่อนไขการชำระเงิน (payment terms)

---

## Sample Data Requirements

**Need 3-5 realistic Chinese supplier invoices** (Jimmy supplies if available)

If not available, generate realistic synthetic samples with:
- Chinese company header (name, address, tax ID)
- Invoice number and date
- Itemized product list (typical factory supplies)
- Subtotal, tax (if any), total in RMB
- Payment terms (e.g., "30 days net")
- Common supplier invoice format

---

## Key Fields to Highlight

Must extract and highlight these in Thai translation:
1. **金额 / 总金额** → จำนวนเงิน (Amount/Total)
2. **日期** → วันที่ (Date)
3. **付款条件 / 付款方式** → เงื่อนไขการชำระเงิน (Payment Terms)

Optional (if time):
4. **发票号** → เลขที่ใบแจ้งหนี้ (Invoice Number)
5. **到期日** → วันครบกำหนด (Due Date)

---

## Build Timeline

### Day 1 (2026-07-08)
- [x] Create demo structure
- [ ] Web upload page (HTML + FastAPI endpoint)
- [ ] Google Vision OCR integration
- [ ] Basic translation (GPT-4)
- [ ] Test with 1 sample invoice

### Day 2 (2026-07-09)
- [ ] PDF generation (bilingual layout)
- [ ] Key field highlighting logic
- [ ] Test with all 3-5 samples
- [ ] Deploy to Railway
- [ ] Write pitch script

---

## Pitch Script (After Build)

**Hook (3 sentences):**
> "Your Chinese suppliers send 10-30 invoices per month. Professional translation costs 300-800 baht per document and takes 1-3 days. This tool translates them instantly for 50-100 baht each—or unlimited for 999-1,999 baht/month."

**Demo Flow (2 minutes):**
1. Show Chinese invoice (real example)
2. Upload to web page
3. Click translate
4. Show bilingual PDF with highlighted key fields
5. "Key numbers—amount, date, terms—automatically highlighted. Ready to process in your accounting system."

**Price Anchor:**
- **Setup:** 5,000-15,000 THB (one-time, includes first 100 translations)
- **Monthly:** 999-1,999 THB unlimited documents
- **Pay-per-doc:** 50-100 THB (vs 300-800 THB human translation)

**Close:**
> "Try it free for 30 days with your real supplier invoices. If it doesn't save you time and money, we part as friends."

---

## Deployment

**URL:** `https://nova-translator-demo.up.railway.app` (TBD)
**Environment Variables:**
- `GOOGLE_VISION_API_KEY` (Jimmy's GCP key)
- `OPENAI_API_KEY` (Jimmy's OpenAI key)

---

## Acceptance Criteria

- [ ] Jimmy uploads Chinese invoice image
- [ ] Gets bilingual PDF in <60 seconds
- [ ] PDF has side-by-side layout (Chinese left, Thai right)
- [ ] Key fields (amount, date, terms) highlighted
- [ ] Total demo run time: <5 minutes
- [ ] No help needed from Howard

---

**Status:** Day 1 in progress
**Blocker:** Need 3-5 Chinese invoice samples (Jimmy supplies or I generate realistic synthetic ones)
