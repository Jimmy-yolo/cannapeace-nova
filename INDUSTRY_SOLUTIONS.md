# NOVA Industry-Specific Automation Solutions

**Purpose:** Ready-to-build automation solutions for top Thai/Bangkok industries
**Strategy:** Target highest-pain, industry-specific problems with 3-5 day builds

---

## Solution Matrix: Top 5 Industries × Top Use Case

| Industry | Top Pain Point | Solution | Build Time | Value Prop |
|----------|----------------|----------|------------|------------|
| **Restaurants** | LINE orders → manual Excel entry | LINE-to-Excel Order Bridge | 3-5 days | Save 2-4 hrs/day |
| **Retail/Wholesale** | Inventory chaos across locations | Multi-Location Inventory Sync | 4-6 days | Real-time stock visibility |
| **Import/Export** | Chinese supplier docs need translation | Thai-Chinese Doc Translator | 3-4 days | 80% cost savings |
| **Accounting Firms** | Thai tax invoices manual data entry | E-Tax Invoice OCR Extractor | 4-5 days | 3+ hrs/month saved |
| **Manufacturing/SME** | Annual DBD filing stress | DBD XBRL Auto-Formatter | 5 days | Avoid 12K-200K THB penalties |

---

## 1. RESTAURANTS: LINE-to-Excel Order & Inventory Bridge

### Problem
Thai restaurants receive 80-90% of orders via LINE, manually re-key into Excel for inventory/COGS tracking.

**Pain Level:** 10/10 (daily, 2-4 hours)
**Market Size:** 8,119 new Chinese-Thai restaurants in Bangkok (2024)
**Uniqueness:** 9/10 (LINE dominance is Thailand-specific)

### Solution Spec
- LINE Official Account bot
- Multilingual parsing (Thai/Chinese/English)
- Auto-updates Google Sheets
- Low-stock alerts
- Daily summary reports

**Tech Stack:**
- LINE Messaging API (free tier)
- OpenAI GPT-4 (order parsing)
- Google Sheets API
- Railway deployment

**Pricing:** 1,500-3,000 THB/month per restaurant

**Full Spec:** `/products/nova/factory-automation/line-order-bridge/PROJECT_SPEC.md`

---

## 2. RETAIL/WHOLESALE: Multi-Location Inventory Sync

### Problem
Retail chains and wholesalers with 2-10 locations track inventory in separate Excel files. Staff call each location daily to check stock before confirming customer orders.

**Pain Level:** 9/10 (daily, 1-2 hours calling + frequent stock-outs)
**Market Size:** Bangkok retail SMEs, especially Chinese-owned chains
**Uniqueness:** 7/10 (multi-location pain is global, but LINE integration is Thai-specific)

### Solution Spec

**What It Does:**
1. Each location updates stock via LINE message or simple web form
2. Central Google Sheet shows real-time stock across all locations
3. Staff check one dashboard instead of calling 10 locations
4. Auto-alerts when total stock low
5. Weekly stock movement reports

**Example Use Cases:**
- Fashion retail: "How many size M blue shirts across all 5 branches?"
- Auto parts wholesale: "Customer wants 20 brake pads, which warehouse has stock?"
- Food distributor: "Tomatoes expiring soon at which location?"

**Tech Stack:**
- LINE bot (for quick updates from each location)
- Web dashboard (for viewing + manual entry)
- Google Sheets (central database, free)
- Railway deployment
- Optional: Barcode scanner integration via phone camera

**Build Timeline:**
- Day 1: LINE bot + Google Sheets structure
- Day 2: Web dashboard (location selection, item update)
- Day 3: Multi-location logic + stock alerts
- Day 4: Reports + location-specific views
- Day 5-6: Testing with 2-3 locations, iteration

**Pricing:** 2,500-5,000 THB/month (scales with # of locations)

**Demo Flow:**
1. Location A staff: LINE message "น้ำตาล 50 kg เหลือ 30 ถุง" (Sugar 50kg, 30 bags left)
2. Dashboard updates instantly
3. HQ staff checks dashboard: sees Location A (30), Location B (15), Location C (45) = Total 90 bags
4. Customer asks for 100 bags → knows to reorder before confirming

**Value Prop:** "Stop calling branches. See all stock in real-time on one screen."

---

## 3. IMPORT/EXPORT: Thai-Chinese Business Document Translator

### Problem
Bangkok businesses with Chinese suppliers receive invoices/POs/contracts in Chinese. Professional translation costs 300-800 THB per document and takes 1-3 days. Daily operations require immediate understanding.

**Pain Level:** 8/10 (daily for active importers, expensive + delays)
**Market Size:** 58.78% of Bangkok restaurants have Chinese investment, plus thousands of import/export SMEs
**Uniqueness:** 8/10 (Chinese-Thai business context is Bangkok-specific)

### Solution Spec

**What It Does:**
1. Accept document images (Chinese invoice, PO, contract) via:
   - LINE bot (forward photo)
   - Web upload (drag & drop)
   - WeChat forward → LINE bot
2. OCR extracts Chinese text (Simplified + Traditional)
3. AI translates to Thai with business terminology accuracy
4. Maintains document structure/formatting
5. Highlights key fields (amounts, dates, payment terms)
6. Exports bilingual PDF (Chinese-Thai side-by-side)
7. Learns from user corrections (crowdsourced improvement)

**Document Types:**
- Commercial invoices (most common)
- Purchase orders
- Packing lists
- Contracts/agreements
- Certificates of origin
- Shipping documents

**Tech Stack:**
- LINE Messaging API (receive photos)
- Google Cloud Vision (Chinese OCR, supports both Simplified/Traditional)
- OpenAI GPT-4 (Chinese→Thai translation with business context)
- PDF generation (bilingual layout)
- Web interface for manual corrections
- Railway deployment

**Build Timeline:**
- Day 1: LINE bot + image upload
- Day 2: OCR integration (Google Vision)
- Day 3: Translation pipeline (GPT-4 with business terminology)
- Day 4: Bilingual PDF generation + key field highlighting
- Day 5: Testing with real supplier documents, iteration

**Pricing Models:**
- **Pay-per-document:** 50-100 THB/document (vs 300-800 THB human translation)
- **Monthly subscription:** 999-1,999 THB/month unlimited documents
- **Enterprise:** 3,000+ THB/month + custom terminology database

**Demo Flow:**
1. Import/export business receives Chinese invoice via WeChat
2. Forward photo to LINE bot
3. Bot replies in 30 seconds: "รับเอกสารแล้ว กำลังแปล..." (Document received, translating...)
4. 2 minutes later: Bilingual PDF ready (Chinese left, Thai right)
5. Key fields highlighted: จำนวนเงิน 15,000 RMB (≈75,000 THB), ครบกำหนด 2026-08-15
6. User spots error in item name translation, corrects via web interface
7. System learns: next time "不锈钢螺丝" correctly translates to "สกรูสแตนเลส" instead of generic "สกรูเหล็ก"

**Value Prop:**
- "Instant translation, 80% cost savings"
- "Understand supplier invoices in 2 minutes, not 2 days"
- "No more waiting for translator to process morning's 10 invoices"

**Network Effects:**
- Import/export community in Bangkok is tight-knit
- One satisfied user refers 3-5 peers
- Chinese supplier invoices have common terminology → translation quality improves fast with volume

---

## 4. ACCOUNTING FIRMS: E-Tax Invoice Data Extractor

### Problem
Thai companies receive 20-100+ supplier tax invoices monthly (PDFs/images via LINE/email). Accountants manually re-key every field (13+ required fields per Thai Revenue Department format) into accounting software. Takes 3-5 minutes per invoice.

**Pain Level:** 8/10 (monthly recurring, expensive labor cost)
**Market Size:** Every Thai registered company (millions), plus all accounting firms serving them
**Uniqueness:** 10/10 (Thai tax invoice format is Thailand-specific)

### Solution Spec

**What It Does:**
1. Accepts Thai tax invoice images/PDFs via:
   - Desktop app (drag & drop folder of 50 invoices)
   - LINE forward (for mobile staff)
   - Email auto-import
2. OCR extracts all 13+ required Thai tax invoice fields:
   - Tax invoice number
   - 13-digit Thai Tax ID (validated with checksum)
   - Date and time
   - Seller name/address
   - Buyer name/address
   - Item descriptions (Thai language)
   - Pre-VAT amount
   - 7% VAT amount
   - Total amount
   - Payment method
3. Validates data (Tax ID checksum, amounts add up correctly)
4. Exports to CSV/Excel compatible with popular Thai accounting software:
   - Express
   - Acc-Soft
   - Money Works
   - TALLY
5. Bulk processing: 50 invoices in 5-10 minutes
6. Manual correction interface for edge cases
7. Audit trail (original image + extracted data)

**Tech Stack:**
- Desktop app: Electron (cross-platform) or web-based
- OCR: Google Cloud Vision API (Thai language support)
- Thai language processing: Custom field extraction rules + GPT-4 fallback
- Tax ID validation: Thai checksum algorithm
- Export: CSV generation compatible with Thai accounting software formats
- Optional: LINE bot for mobile invoice forwarding

**Build Timeline:**
- Day 1: Thai tax invoice template recognition (identify fields)
- Day 2: OCR integration + Thai text extraction
- Day 3: Field extraction logic + Tax ID validation
- Day 4: CSV export to accounting software formats
- Day 5: Bulk processing + manual correction UI

**Pricing:**
- **Solo accountant:** 500-1,000 THB/month (up to 100 invoices/month)
- **Accounting firm:** 2,000-5,000 THB/month (unlimited invoices, multi-user)
- **Enterprise:** 10,000+ THB/month (API access, custom integrations)

**Demo Flow:**
1. Accountant receives 50 supplier invoices via email (mix of PDF/images)
2. Drag & drop folder into desktop app
3. App processes all 50 in 8 minutes:
   - OCR extracts all fields
   - Validates Tax IDs (flags 2 invalid ones)
   - Checks amount calculations (flags 1 mismatch)
4. Accountant reviews 3 flagged invoices (2 min each = 6 min total)
5. Exports to CSV, imports into Express accounting software (2 min)
6. **Total time: 16 minutes vs 200+ minutes manual (92% time savings)**

**Value Prop:**
- "Process 50 invoices in 10 minutes instead of 3+ hours"
- "Eliminate data entry errors (Tax ID checksum validation)"
- "Works with the accounting software you already use"

**Government Incentive:** 200% tax deduction for SME digital tools (2025-2027) makes this an easy CFO approval.

---

## 5. ALL SMEs: DBD Financial Statement Auto-Formatter

### Problem
Every Thai company must submit annual financial statements to the Department of Business Development (DBD) in XBRL format via Excel templates. Accountants spend 4-8 hours manually copying data from accounting software into DBD's specific Excel template. Even 1-day late filing = 12,000-200,000 THB fines.

**Pain Level:** 7/10 (annual, but extremely stressful + high penalty risk)
**Market Size:** Every Thai registered company (millions)
**Uniqueness:** 10/10 (DBD XBRL Excel format is Thailand-only)

### Solution Spec

**What It Does:**
1. Imports financial data from common Thai accounting software formats (CSV/Excel exports)
2. Auto-maps Chart of Accounts to DBD XBRL categories using AI:
   - "เงินสดในมือ" → Cash on Hand
   - "เจ้าหนี้การค้า" → Trade Payables
   - Handles company-specific account naming variations
3. Fills DBD Excel template in correct format (different templates for different entity types)
4. Validates balance sheet equations (Assets = Liabilities + Equity)
5. Generates required PDF attachments
6. Provides pre-submission checklist (Thai/Chinese/English)
7. Email reminders 90/60/30 days before deadline
8. Stores 3-year history for comparison

**Entity Types Supported:**
- Limited companies (บริษัทจำกัด)
- Partnerships (ห้างหุ้นส่วนจำกัด)
- Public companies (บริษัทมหาชน)

**Tech Stack:**
- Web-based tool (no installation needed)
- Account mapping: GPT-4 + rule-based logic
- DBD Excel template parsing (openpyxl/exceljs)
- Balance sheet validation logic
- PDF generation (reportlab/puppeteer)
- Email automation (SendGrid)
- Secure storage (encrypted financial data)

**Build Timeline:**
- Day 1: Parse DBD Excel templates (all entity types)
- Day 2: Account mapping logic (rule-based for common accounts)
- Day 3: Balance sheet validation + Excel generation
- Day 4: PDF attachments + pre-submission checklist
- Day 5: Email reminders + historical comparison

**Pricing:**
- **Per filing:** 1,500-3,000 THB/filing (cheaper than accountant's 4-8 hours)
- **Annual subscription:** 5,000-8,000 THB/year (includes reminders + updates to DBD template changes)
- **Accounting firm:** 50,000+ THB/year (unlimited clients)

**Demo Flow:**
1. Accountant exports Trial Balance from Express accounting software (CSV file)
2. Uploads to web tool, selects company type (บริษัทจำกัด)
3. Tool auto-maps 90% of accounts correctly, flags 5 ambiguous ones
4. Accountant reviews 5 mappings (2 min each = 10 min)
5. Tool generates DBD-compliant Excel file
6. Accountant reviews final numbers (5 min)
7. Tool generates required PDFs
8. **Total time: 20 minutes vs 4-8 hours manual (90%+ time savings)**
9. Submits to DBD e-Filing with confidence (no late filing risk)

**Value Prop:**
- "4-8 hours → 20 minutes"
- "Never risk 12,000-200,000 THB late filing penalty again"
- "Auto-reminders 90 days before deadline"
- "Works with your existing accounting software"

**Compliance Edge:** DBD template changes annually → tool auto-updates (vs manual template hunting).

---

## Go-to-Market Strategy by Industry

### Restaurants (LINE-to-Excel)
- **Target:** Chinese-Thai restaurants in Bangkok (Yaowarat, Silom, Sukhumvit)
- **Channel:** Facebook groups (Bangkok Chinese Restaurants, Thai Restaurant Owners), WeChat moments
- **Hook:** "Stop wasting 2 hours daily re-typing LINE orders"
- **Demo:** 5-min LINE chat demo on their phone
- **Close:** Free 30-day trial → 1,500 THB/month

### Retail (Multi-Location Inventory)
- **Target:** Fashion retail chains, auto parts wholesalers, food distributors with 2-10 locations
- **Channel:** Trade shows, retail associations, direct outreach
- **Hook:** "Stop calling branches. See all stock in real-time."
- **Demo:** Setup with their 2-3 locations in 1 hour, live test
- **Close:** 2,500-5,000 THB/month based on location count

### Import/Export (Thai-Chinese Translator)
- **Target:** Bangkok Chinatown import/export businesses, Chinese restaurant suppliers
- **Channel:** Import/export associations, referrals (tight-knit community)
- **Hook:** "Translate Chinese invoices instantly, save 80%"
- **Demo:** Live translation of their actual supplier invoice (2 min)
- **Close:** 999-1,999 THB/month unlimited OR 50-100 THB/document

### Accounting Firms (E-Tax OCR)
- **Target:** Mid-size accounting firms (10-50 staff) serving 50-200 SME clients
- **Channel:** Accountant associations, LinkedIn, accounting software resellers
- **Hook:** "Process 50 tax invoices in 10 minutes, not 3 hours"
- **Demo:** Batch process 20 real invoices (show 92% time savings)
- **Close:** 2,000-5,000 THB/month for firm-wide access

### All SMEs (DBD Filing)
- **Target:** Accountants, CFOs, business owners 90 days before DBD deadline (peaks in Feb-Apr)
- **Channel:** Google Ads ("ยื่นงบการเงิน DBD"), accounting associations, email campaigns
- **Hook:** "Avoid 12,000-200,000 THB late filing penalty"
- **Demo:** Upload trial balance, get DBD-ready Excel in 20 min
- **Close:** 1,500-3,000 THB one-time filing fee OR 5,000-8,000 THB annual

---

## Week 1 Execution Plan

**Option A: Build One Full Solution (LINE-to-Excel)**
- Days 1-5: Build LINE-to-Excel Order Bridge MVP
- Test with factory or 1 pilot restaurant
- Document case study
- Start outreach Week 2

**Option B: Build Templates for All 5**
- Days 1-5: Create detailed specs + technical blueprints for all 5 solutions
- Pick 2-3 highest-interest from outreach responses
- Build chosen solutions Weeks 2-4

**Recommended: Option A**
- Faster time-to-revenue (1 working solution beats 5 specs)
- Real testimonial beats hypothetical value props
- LINE-to-Excel is highest pain + fastest build

---

**All 5 solutions are ready to build. Which industry do you want to target first?**
