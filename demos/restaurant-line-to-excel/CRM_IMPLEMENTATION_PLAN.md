# CannaPeace CRM Implementation Plan

## Current Data Storage Analysis

### ✅ What You Have NOW

#### 1. **Order Data** (Saved to Google Sheets)
Currently saved when customer completes an order:
- ✅ Timestamp
- ✅ Customer name
- ✅ Phone number
- ✅ Items ordered
- ✅ Total amount
- ✅ Delivery address + notes

**Location:** Google Sheet (ID: `1Rz1DbllW-...`)

#### 2. **Conversation History** (In-Memory Only)
Currently stored in RAM while bot is running:
- ✅ User messages
- ✅ Bot responses
- ✅ Conversation context (last 10 messages)

**Problem:** Lost when bot restarts! ❌

#### 3. **LINE User ID**
Available but NOT currently saved:
- LINE user ID (unique identifier like `U1234567890abc`)
- Available in `event.source.user_id`

### ❌ What You DON'T Have (Yet)

- ❌ Persistent chat history (messages are lost on restart)
- ❌ Customer profiles (linking phone → LINE user ID)
- ❌ Customer lifetime value (total spent, order count)
- ❌ Customer preferences (favorite strains, order patterns)
- ❌ Contact history (when they last messaged)
- ❌ Customer segments (VIP, new, inactive, etc.)

---

## CRM System Design

### What is CRM?
**Customer Relationship Management** - A system to:
1. Track all customer interactions
2. Build customer profiles
3. Analyze customer behavior
4. Enable personalized marketing
5. Improve customer service

### Proposed Architecture

#### Option A: Google Sheets-Based CRM (Simple, Quick)
**Best for:** Getting started quickly, small-medium customer base

**Structure:**
```
Sheet 1: Orders (existing)
- Timestamp, Name, Phone, Items, Total, Address

Sheet 2: Customers (NEW!)
- LINE User ID
- Phone Number
- Customer Name
- First Order Date
- Last Order Date
- Total Orders
- Lifetime Value
- Favorite Strains
- Tags (VIP, Inactive, etc.)

Sheet 3: Messages (NEW!)
- Timestamp
- LINE User ID
- Message Type (user/bot)
- Message Content
- Session ID
```

**Pros:**
- ✅ Easy to implement (already using Google Sheets)
- ✅ Visual (can open in browser)
- ✅ No new infrastructure
- ✅ Works with existing setup

**Cons:**
- ❌ Slower for large datasets (1000+ customers)
- ❌ Limited analytics capabilities
- ❌ Manual data processing

#### Option B: Database CRM (Advanced, Scalable)
**Best for:** Long-term growth, advanced features

**Structure:**
```sql
Table: customers
- id (auto)
- line_user_id (unique)
- phone
- name
- first_seen
- last_seen
- total_orders
- lifetime_value
- tags

Table: orders
- id (auto)
- customer_id (foreign key)
- timestamp
- items (JSON)
- total
- address
- status

Table: messages
- id (auto)
- customer_id (foreign key)
- timestamp
- sender (user/bot)
- content
- session_id
```

**Tech Stack:**
- PostgreSQL (Railway provides free tier)
- Prisma ORM (easy TypeScript/Python integration)

**Pros:**
- ✅ Fast queries, scalable
- ✅ Advanced analytics
- ✅ Relational data
- ✅ Better for automation

**Cons:**
- ❌ More complex setup
- ❌ Requires database management
- ❌ Migration from current system

---

## Recommended Implementation: Hybrid Approach

**Phase 1: Enhance Current Google Sheets** (Quick Win)
1. Add LINE User ID to order data
2. Create Customers sheet with profiles
3. Save key conversation events

**Phase 2: Add Message Logging** (Build History)
1. Save all messages to Messages sheet
2. Link to customer profiles
3. Enable conversation search

**Phase 3: Analytics & Insights** (Business Intelligence)
1. Customer lifetime value calculations
2. Strain popularity analysis
3. Customer segmentation
4. Automated follow-ups

**Phase 4: Optional Database Migration** (Scale)
1. Move to PostgreSQL when > 1000 customers
2. Keep Google Sheets as backup/export

---

## Phase 1 Implementation Plan (Quick Start)

### Changes Needed to `app.py`

#### 1. Add LINE User ID to Order Data
```python
# Current (app.py line ~474):
row = [
    datetime.now().isoformat(),
    order_data.get("customer_name", "Customer"),
    order_data.get("phone", "Not provided"),
    items_str,
    order_data["total"],
    order_data.get("address", "") + " " + order_data.get("notes", "")
]

# Enhanced:
row = [
    datetime.now().isoformat(),
    user_id,  # LINE User ID (NEW!)
    order_data.get("customer_name", "Customer"),
    order_data.get("phone", "Not provided"),
    items_str,
    order_data["total"],
    order_data.get("address", "") + " " + order_data.get("notes", ""),
    "completed"  # Order status (NEW!)
]
```

#### 2. Create/Update Customer Profile
After each order, update customer profile:
```python
# Check if customer exists in Customers sheet
# If not, create new row
# If yes, update: last_order_date, total_orders++, lifetime_value

customer_row = [
    user_id,
    order_data.get("phone"),
    order_data.get("customer_name"),
    datetime.now().isoformat(),  # first_seen (if new)
    datetime.now().isoformat(),  # last_seen
    1,  # total_orders (increment if existing)
    order_data["total"],  # lifetime_value (add if existing)
    "",  # favorite_strains (calculate from orders)
    ""   # tags
]
```

#### 3. Save Key Conversation Events
```python
# Log important events to Messages sheet:
# - New customer contact
# - Order placed
# - Strain inquiries
# - Customer issues

def log_message(user_id, message_type, content, event_type="message"):
    message_row = [
        datetime.now().isoformat(),
        user_id,
        message_type,  # "user" or "bot"
        content[:200],  # Truncate long messages
        event_type  # "message", "order", "strain_inquiry"
    ]
    # Append to Messages sheet
```

### New Google Sheets Structure

#### Sheet 1: Orders (Enhanced)
```
| Timestamp | LINE_User_ID | Name | Phone | Items | Total | Address | Status |
|-----------|--------------|------|-------|-------|-------|---------|--------|
```

#### Sheet 2: Customers (NEW!)
```
| LINE_User_ID | Phone | Name | First_Seen | Last_Seen | Total_Orders | Lifetime_Value | Favorite_Strains | Tags |
|--------------|-------|------|------------|-----------|--------------|----------------|------------------|------|
```

#### Sheet 3: Messages (NEW! - Optional Phase 2)
```
| Timestamp | LINE_User_ID | Type | Content | Event_Type |
|-----------|--------------|------|---------|------------|
```

---

## What You Can Build with CRM Data

### 1. Customer Insights Dashboard

**In Google Sheets (using formulas):**
- Total customers
- Active customers (ordered in last 30 days)
- Top 10 customers by lifetime value
- Most popular strains
- Average order value
- Customer retention rate

**Example Formulas:**
```
Total Customers: =COUNTA(Customers!A:A)
Total Revenue: =SUM(Orders!F:F)
Avg Order Value: =AVERAGE(Orders!F:F)
Top Strain: =INDEX(most frequent strain from orders)
```

### 2. Customer Segmentation

**Automatic tags based on behavior:**
- 🌟 **VIP**: Lifetime value > 5,000฿
- 🆕 **New**: First order < 7 days ago
- ⚠️ **At Risk**: Last order > 60 days ago
- 🔥 **Frequent**: > 5 orders total
- 💤 **Inactive**: Last order > 90 days ago

### 3. Personalized Marketing

**Use CRM data for:**
- Send promotions for favorite strains
- Re-engagement campaigns for inactive customers
- Birthday/anniversary discounts
- Loyalty rewards for VIP customers
- New strain announcements to frequent buyers

### 4. Business Analytics

**Track over time:**
- Customer acquisition rate
- Customer lifetime value trends
- Strain popularity by month
- Revenue by customer segment
- Repeat purchase rate
- Average time between orders

---

## Implementation Steps

### Step 1: Update Sheet Structure (Manual)

1. Open your Google Sheet
2. Rename "Sheet1" to "Orders"
3. Add column headers:
   ```
   Timestamp | LINE_User_ID | Name | Phone | Items | Total | Address | Status
   ```
4. Create new sheet "Customers" with headers:
   ```
   LINE_User_ID | Phone | Name | First_Seen | Last_Seen | Total_Orders | Lifetime_Value | Favorite_Strains | Tags
   ```

### Step 2: Update Code (I can do this for you!)

Modify `app.py` to:
- ✅ Save LINE User ID with each order
- ✅ Create/update customer profile after each order
- ✅ Add order status field
- ✅ Link orders to customer profiles

### Step 3: Create Dashboard (Google Sheets Formulas)

Add a "Dashboard" sheet with:
- Customer count
- Total revenue
- Active customers
- Popular strains
- Recent orders

### Step 4: Optional - Message Logging

Add "Messages" sheet and log:
- All customer messages
- Bot responses
- Conversation context

---

## Privacy & Data Considerations

### Data Storage
- ✅ **LINE User ID**: Anonymous identifier, safe to store
- ✅ **Phone**: Customer provided, with consent (for orders)
- ✅ **Messages**: Consider privacy policy for chat logging

### GDPR/Privacy Compliance
- Allow customers to request data deletion
- Don't store sensitive health information
- Use data only for order fulfillment and service improvement
- Provide privacy policy (if logging messages)

### Data Security
- ✅ Google Sheets access restricted to your Google account
- ✅ LINE User IDs are encrypted by LINE
- ⚠️ Don't share spreadsheet publicly

---

## Cost & Performance

### Google Sheets Limits
- **Free tier:** 5 million cells
- **Performance:** Good up to ~10,000 orders
- **API quota:** 100 requests per 100 seconds

### Estimated Capacity
- 10,000 customers × 10 columns = 100,000 cells
- 50,000 orders × 8 columns = 400,000 cells
- **Total: ~500,000 cells** (10% of free tier)

**Conclusion:** Google Sheets will work fine for 1-2 years!

---

## Next Steps - Choose Your Level

### Level 1: Minimal (15 minutes)
- ✅ Just add LINE User ID to order data
- Enables linking orders to customers manually

### Level 2: Standard (1 hour) ⭐ RECOMMENDED
- ✅ Add LINE User ID to orders
- ✅ Create Customers sheet with profiles
- ✅ Auto-update customer lifetime value
- ✅ Add order status tracking

### Level 3: Advanced (3 hours)
- ✅ Everything in Level 2
- ✅ Message logging to Messages sheet
- ✅ Customer segmentation (VIP, New, etc.)
- ✅ Analytics dashboard

### Level 4: Enterprise (Full Day)
- ✅ Everything in Level 3
- ✅ Migrate to PostgreSQL database
- ✅ Advanced analytics with charts
- ✅ Automated marketing campaigns

---

## Would You Like Me To Implement This?

I can build **Level 2 (Standard CRM)** right now:
1. Update `app.py` to save LINE User ID with orders
2. Create customer profiles automatically
3. Track lifetime value and order count
4. Update Google Sheets structure

This will give you:
- ✅ Customer database
- ✅ Order history per customer
- ✅ Basic analytics
- ✅ Foundation for future features

**Want me to proceed with Level 2?** It's the sweet spot - gets you CRM capabilities without complexity!
