# Session Handoff - CRM Implementation Priority

## Context for Next Session

**Date:** 2026-07-14
**Status:** v1.0 renamed to CannaPeace AI Platform, ready for v2.0 CRM implementation

---

## Strategy Decided: CRM First ✅

**Approach:** Build closed-loop, fully structured system FIRST, then add modular expansions

**Why:**
- Solid foundation before multi-channel expansion
- Complete customer data model
- Attribution tracking from day 1
- Then plug in Messenger, Instagram, TikTok as modules

---

## What's Complete (This Session)

### 1. Project Renamed ✅
- **Old:** restaurant-line-to-excel
- **New:** cannapeace-ai-platform
- **Path:** `/Users/jimmy/CannaPeace/products/nova/demos/cannapeace-ai-platform`
- **Git:** All history preserved via `git mv`
- **Tags:** v1.0.0, v1.0.1 exist

### 2. Production Status ✅
- **Live:** https://cannapeace-nova-production.up.railway.app
- **Features:** LINE bot, Claude AI, strain images, orders to Google Sheets, typing indicator
- **Health:** All systems operational

### 3. Documentation Created ✅
- `MIGRATION_TO_ADVANCED_CRM.md` - How to build v2.0 on v1.0
- `OMNICHANNEL_EXPANSION_ROADMAP.md` - Future Messenger/Instagram/TikTok/social auto-reply
- `CRM_IMPLEMENTATION_PLAN.md` - 4 levels of CRM
- Advanced CRM design in `/Users/jimmy/CannaPeace/outputs/` (6 docs, 154KB)

### 4. Current Code Base
- **app.py:** 744 lines, FastAPI, LINE SDK, Claude AI, Google Sheets
- **Architecture:** Solid foundation, ready to extend
- **No rewrite needed:** Just add features incrementally

---

## Next Session: Implement v2.0 CRM

### Goal
**Closed-loop system with:**
- Customer profiles (unified across future channels)
- Persistent conversation history
- Journey tracking (7 stages)
- Attribution tracking (multi-channel ready)
- Lifetime value calculation
- Customer segmentation

### Implementation Plan (Week 1-3)

#### Phase 1: Enhanced Data Model (Week 1)
**Google Sheets structure:**

**Sheet 1: Orders (add columns)**
```
Timestamp | LINE_User_ID | Name | Phone | Items | Total | Address | Status | Attribution_Source
```

**Sheet 2: Customers (NEW!)**
```
LINE_User_ID | Phone | Name | First_Seen | Last_Seen | Total_Orders | Lifetime_Value |
Acquisition_Source | Current_Journey_Stage | Segment | Favorite_Strains | Tags
```

**Sheet 3: Messages (NEW!)**
```
Timestamp | LINE_User_ID | Direction | Content | Detected_Intent | Journey_Stage_Before | Journey_Stage_After
```

**Sheet 4: Journey_Events (NEW!)**
```
Event_ID | LINE_User_ID | Event_Type | From_Stage | To_Stage | Timestamp | Metadata
```

**Code changes:** ~100 lines
- Add LINE User ID to order save
- Create customer profile on first contact
- Update customer stats on each order

#### Phase 2: Customer Profiles (Week 2)
**New functions:**
```python
def create_customer_profile(user_id, phone, name, attribution_source)
def update_customer_profile(user_id, order_data)
def calculate_customer_segment(user_id)  # VIP, repeat, new, at-risk, inactive
def get_customer_lifetime_value(user_id)
```

**Code changes:** ~150 lines

#### Phase 3: Journey Tracking (Week 2-3)
**7 stages:**
1. Initial Contact
2. Menu Inquiry
3. Product Question
4. Address Collection
5. Order Intent
6. Order Placement
7. Completion

**Functions:**
```python
def detect_journey_stage(message_text, conversation_history)
def log_journey_event(user_id, from_stage, to_stage)
def update_current_stage(user_id, new_stage)
```

**Code changes:** ~150 lines

#### Phase 4: Persistent History (Week 3)
**Replace in-memory with Google Sheets:**
```python
def save_message(user_id, direction, content, intent)
def load_conversation_history(user_id, limit=10)
```

**Code changes:** ~100 lines

**Total new code:** ~500 lines (744 → ~1,200 lines)

---

## Key Files to Reference

### Current System
```
app.py - Main bot logic (744 lines)
customer_config.json - Product catalog (7 strains)
.env.example - Environment variables template
railway.json - Deployment config
```

### Documentation
```
MIGRATION_TO_ADVANCED_CRM.md - Implementation guide
CRM_IMPLEMENTATION_PLAN.md - 4 CRM levels
/Users/jimmy/CannaPeace/outputs/LINE_CRM_MARKETING_SYSTEM_DESIGN.md - Complete design (75 pages)
```

---

## Environment Variables (Railway)

**Current:**
- `LINE_CHANNEL_SECRET` - Set ✅
- `LINE_CHANNEL_ACCESS_TOKEN` - Set ✅
- `ANTHROPIC_API_KEY` - Set ✅
- `GOOGLE_CREDENTIALS_BASE64` - Set ✅
- `GOOGLE_SHEET_ID` - Set ✅ (1Rz1DbllW-...)
- `PUBLIC_URL` - Set ✅

**No new variables needed for CRM!** (Uses same Google Sheet)

---

## Google Sheet Setup (Week 1 Task)

### Step 1: Open existing sheet
Sheet ID: `1Rz1DbllW-...` (get from Railway env vars)

### Step 2: Add columns to "Orders" sheet
Current columns: Timestamp, Name, Phone, Items, Total, Address

Add: `LINE_User_ID`, `Status`, `Attribution_Source`, `UTM_Campaign`, `UTM_Medium`, `UTM_Source`

### Step 3: Create new sheets
1. Create "Customers" sheet
2. Create "Messages" sheet
3. Create "Journey_Events" sheet
4. Create "Attribution_Links" sheet (for future)

### Step 4: Add headers
(Exact column names provided in Phase 1 above)

---

## Code Changes Roadmap

### Week 1: Data Model
1. Update `save_to_sheets()` in app.py to include LINE User ID
2. Test with one manual order
3. Verify LINE User ID appears in sheet

### Week 2: Customer Profiles
1. Add `create_customer_profile()` function
2. Add `update_customer_profile()` function
3. Call on each order completion
4. Test: Place order, see customer profile created

### Week 3: Journey + History
1. Add `detect_journey_stage()` function
2. Add `save_message()` function
3. Replace `conversation_memory` dict with Sheets load
4. Test: Have conversation, restart bot, history persists

### Week 4: Testing & Polish
1. Test full customer journey
2. Verify all data saves correctly
3. Create simple analytics queries
4. Deploy to production

---

## Success Metrics (v2.0 CRM)

After implementation, you'll have:

✅ **Customer profiles** - Every LINE user tracked
✅ **Order history** - All orders linked to customer
✅ **Lifetime value** - Auto-calculated per customer
✅ **Customer segments** - VIP, repeat, new, at-risk, inactive
✅ **Journey tracking** - Know where customers drop off
✅ **Persistent history** - Conversations survive restarts
✅ **Attribution ready** - Foundation for multi-channel tracking

**Then:** Plug in Messenger, Instagram, TikTok as modules (they'll use same customer profiles!)

---

## After CRM (Future Modules)

### Module 1: Facebook Messenger (Week 5-7)
- Plug into existing customer profiles
- Same Claude AI
- Same Google Sheets backend
- Just add Messenger API adapter

### Module 2: Instagram DM (Week 8-9)
- Same approach as Messenger
- Reuse 90% of code

### Module 3: TikTok + Social Auto-Reply (Week 10-14)
- TikTok chat integration
- Comment classification AI
- Auto-reply system

**All modules share the CRM foundation you're building now!**

---

## Quick Start Commands (Next Session)

```bash
# Navigate to project
cd /Users/jimmy/CannaPeace/products/nova/demos/cannapeace-ai-platform

# Check current status
git status
git log --oneline -5

# Open in editor
code .  # or your preferred editor

# View current production
curl https://cannapeace-nova-production.up.railway.app/health | python3 -m json.tool

# Check Railway
railway status
railway logs | head -20
```

---

## First Tasks Next Session

1. **Open Google Sheet** - Add 4 new sheets + columns
2. **Update app.py** - Add LINE User ID to order save (~10 lines)
3. **Test** - Place one order, verify user ID saved
4. **Create customer profile function** - ~50 lines
5. **Test** - Place order, verify profile created

**Estimate:** 2-3 hours to get basic CRM working!

---

## Questions to Resolve Next Session

- [ ] Confirm Google Sheet structure (I'll provide exact schema)
- [ ] Choose customer segment logic (VIP = how much lifetime value?)
- [ ] Journey stage detection rules (what triggers each stage?)
- [ ] Message retention policy (keep last 10? 50? All?)

---

## Context for Claude (Next Session)

**User wants:** CRM implementation to create closed-loop system before adding multi-channel modules

**Current state:**
- v1.0 LINE bot working in production
- Project renamed to cannapeace-ai-platform
- Ready to extend with customer profiles + journey tracking

**Priority:** Build solid CRM foundation (Week 1-4), then add Messenger/Instagram/TikTok as plug-in modules

**Approach:** Incremental enhancement (not rewrite), ship improvements every week

**Files to read first:**
1. `MIGRATION_TO_ADVANCED_CRM.md` - Implementation strategy
2. `app.py` lines 1-100 - Understand current structure
3. `/Users/jimmy/CannaPeace/outputs/LINE_CRM_MARKETING_SYSTEM_DESIGN.md` - Complete design reference

---

## Summary

**Done This Session:**
- ✅ Renamed to CannaPeace AI Platform
- ✅ Documented full omnichannel vision
- ✅ Created CRM implementation roadmap
- ✅ Decision: CRM first, then modules

**Next Session:**
- 🎯 Implement v2.0 CRM (4 weeks)
- 🎯 Create customer profiles
- 🎯 Track customer journey
- 🎯 Build closed-loop system

**Then:** Add Messenger, Instagram, TikTok, social auto-reply as modules on top of solid CRM foundation

**Ready to resume implementation!** 🚀
