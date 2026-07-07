# LINE-to-Excel Order & Inventory Bridge — Factory Automation Project

**Status:** Week 1 Design
**Type:** First Portfolio Project (Free for Family Factory)
**Timeline:** 3-5 days to MVP
**Purpose:** Demonstrate bilingual automation capability + create case study

---

## Problem Statement

Thai restaurants and retail businesses receive 80-90% of customer orders via LINE Official Account, but manually re-key every order into Excel spreadsheets for inventory tracking and COGS calculations.

**Current Pain:**
- Staff screenshot or copy LINE orders (Thai/Chinese/English mixed)
- Manually type into Excel inventory sheet (30-60 seconds per order)
- Re-calculate stock levels manually
- Update COGS in separate spreadsheet
- **Family factory: ~50-100 orders/day = 2-3 hours daily waste**
- **Error rate: High (wrong items, quantities, pricing)**

---

## Deliverable

A LINE Official Account chatbot + backend system that:

1. **Captures Orders via LINE**
   - Customers/staff send order messages to LINE bot
   - Supports Thai/Chinese/English text
   - Handles common formats: "ไก่ย่าง 5 ตัว", "烤鸡 5只", "5x Grilled Chicken"

2. **Auto-Parses Order Details**
   - Extracts: item name, quantity, variant/size
   - Maps to inventory SKUs using fuzzy matching
   - Handles typos and variations ("ไก่ยาง" vs "ไก่ย่าง")

3. **Updates Excel/Google Sheets in Real-Time**
   - Adds order to daily orders sheet
   - Deducts from inventory stock levels
   - Calculates remaining stock
   - Updates COGS automatically

4. **Sends Alerts via LINE**
   - Confirms order received (to customer)
   - Alerts staff when stock low (<10 units)
   - Daily summary report at end of day

---

## Tech Stack (3-5 Day Build)

### Backend
- **Platform:** Railway (free tier sufficient for MVP)
- **Language:** Node.js or Python (pick based on LINE SDK quality)
- **Framework:** Express.js or FastAPI

### APIs & Services
- **LINE Messaging API** (free tier: unlimited replies)
  - Webhook for incoming messages
  - Reply API for confirmations
- **OpenAI API** (GPT-4 for multilingual NLP)
  - Parse mixed Thai/Chinese/English orders
  - Extract: item, quantity, variant
- **Google Sheets API** or **Excel file sync**
  - Real-time updates
  - No database needed initially

### Data Flow
```
Customer → LINE message → Webhook → Backend
           ↓
      OpenAI parse (Thai/Zh/EN)
           ↓
      Match to inventory SKUs
           ↓
      Update Google Sheets
           ↓
      Reply confirmation to LINE
```

---

## Data In / Data Out

### Input (LINE Messages)
Examples:
- Thai: "สั่งไก่ย่าง 5 ตัว กะปริก 3 จาน"
- Chinese: "要烤鸡5只，泰式炒河粉3份"
- English: "5 grilled chicken, 3 pad thai"
- Mixed: "ไก่ย่าง 5, pad thai 3份"

### Output (Google Sheets)

**Sheet 1: Daily Orders**
| Time | Item Thai | Item EN | Qty | Unit Price | Total | Customer |
|------|-----------|---------|-----|------------|-------|----------|
| 14:32 | ไก่ย่าง | Grilled Chicken | 5 | 45 | 225 | LINE:user123 |

**Sheet 2: Inventory**
| SKU | Item Thai | Item EN | Stock Before | Stock After | Reorder Level |
|-----|-----------|---------|--------------|-------------|---------------|
| CH001 | ไก่ย่าง | Grilled Chicken | 50 | 45 | 10 |

**Sheet 3: COGS**
| Date | Item | Qty Sold | Unit Cost | Total Cost |
|------|------|----------|-----------|------------|
| 2026-07-08 | Grilled Chicken | 5 | 28 | 140 |

---

## MVP Feature List (Week 1)

### Must Have (Build First)
- [ ] LINE bot receives messages
- [ ] GPT-4 parses Thai/English orders (start with these 2)
- [ ] Updates Google Sheets (orders + inventory)
- [ ] Replies confirmation to customer
- [ ] Low stock alert (when qty < 10)

### Should Have (Add if time)
- [ ] Chinese language support
- [ ] Daily summary report
- [ ] Handle order cancellations
- [ ] Admin command (/status, /inventory)

### Won't Have (V2 Later)
- ❌ Payment processing (manual for now)
- ❌ Complex menu variations (size, spice level)
- ❌ Customer CRM tracking
- ❌ Multi-location support

---

## Acceptance Test

**Scenario:** Customer orders via LINE, inventory updates automatically

1. Send LINE message: "ไก่ย่าง 5 ตัว"
2. Bot replies: "✅ รับออเดอร์แล้ว: ไก่ย่าง 5 ตัว (225 บาท)"
3. Google Sheets "Daily Orders" adds row with timestamp
4. Google Sheets "Inventory" deducts 5 from ไก่ย่าง stock
5. If stock drops below 10, sends alert: "⚠️ ไก่ย่าง เหลือ 8 ตัว กรุณาสั่งเพิ่ม"
6. Process takes <5 seconds from message to sheet update

---

## Before/After Metrics (For Case Study)

### Before (Manual Process)
- **Time per order:** 30-60 seconds
- **50 orders/day:** 25-50 minutes
- **Monthly time waste:** 12-25 hours
- **Error rate:** ~10% (wrong quantities, missed orders)
- **Stock-out incidents:** 2-3 times/month

### After (Automated)
- **Time per order:** 5 seconds (just send LINE message)
- **50 orders/day:** 4 minutes (mostly just customer messages)
- **Monthly time saved:** 10-22 hours
- **Error rate:** <1% (typo-tolerant AI parsing)
- **Stock-out incidents:** 0 (real-time alerts)

**ROI:** Saves 10-22 hours/month = 150-330 hours/year at ~200 THB/hour = **30,000-66,000 THB annual value**

---

## Implementation Plan (3-5 Days)

### Day 1: LINE Bot Setup
- [ ] Create LINE Official Account
- [ ] Set up webhook endpoint on Railway
- [ ] Echo bot (receive message → reply same message)
- [ ] Test with Thai/English messages

### Day 2: Order Parsing
- [ ] Integrate OpenAI GPT-4 API
- [ ] Build prompt for order parsing (Thai/English)
- [ ] Test parsing accuracy on sample orders
- [ ] Create item SKU mapping (10-20 common items)

### Day 3: Google Sheets Integration
- [ ] Set up Google Sheets API credentials
- [ ] Create template sheets (Orders, Inventory, COGS)
- [ ] Implement append to Orders sheet
- [ ] Implement deduction from Inventory sheet
- [ ] Test full flow: LINE → parse → sheets update

### Day 4: Confirmations & Alerts
- [ ] Reply confirmation message after order
- [ ] Check inventory levels after update
- [ ] Send low-stock alert if qty < 10
- [ ] Format messages in Thai (nice formatting)

### Day 5: Testing & Documentation
- [ ] Test with 20+ real order variations
- [ ] Handle edge cases (unknown items, typos)
- [ ] Screenshot before/after for case study
- [ ] Write 1-page handover doc (Thai)
- [ ] Record 2-min demo video

---

## Family Factory Specifics (Customize)

**Current Setup:**
- Business type: [Jimmy fills: restaurant? retail? manufacturing?]
- Order volume: [~X orders/day]
- Common items: [List top 10-20 items with Thai/Chinese/English names]
- Current process: [How do they track orders now?]

**Inventory Items Template:**
| SKU | Thai Name | Chinese Name | English Name | Current Stock | Reorder Level |
|-----|-----------|--------------|--------------|---------------|---------------|
| | | | | | |

---

## Case Study Outline (Write After Build)

### Title
"LINE-to-Excel Order Automation Saves Family Factory 2+ Hours Daily"

### Problem (1 paragraph)
"Before automation, staff spent 2-3 hours daily manually copying LINE orders into Excel..."

### Solution (1 paragraph)
"Built a LINE chatbot that understands Thai/English orders and updates inventory automatically..."

### Results (Bullet points)
- ⏱️ Time saved: 2-3 hours → 5 minutes daily (95% reduction)
- 📊 Error rate: 10% → <1%
- 🚨 Stock-outs: 2-3/month → 0
- 💰 Annual value: 30,000-66,000 THB

### Screenshots (3-4 images)
1. Before: Photo of staff manually typing into Excel
2. After: LINE message auto-updating sheet (screen recording)
3. Low-stock alert notification
4. Daily summary report

### Testimonial (Get quote)
"[Owner quote in Thai about time saved and accuracy improvement]"

---

## Next Steps After MVP

1. **Deploy to family factory** (Week 1 end)
2. **Monitor for 1 week** (collect real usage data)
3. **Iterate based on feedback** (fix parsing errors)
4. **Document case study** (screenshots + before/after metrics)
5. **Create demo video** (Thai/Chinese/English versions)
6. **Start Week 2 outreach** (use factory case study)

---

**Build Start:** TBD (Jimmy confirms factory details)
**Target Completion:** 2026-07-14 (end of Week 1)
**Evidence Folder:** `line-order-bridge/evidence/`
