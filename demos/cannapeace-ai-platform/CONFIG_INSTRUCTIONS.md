# Customer Config Setup — Restaurant LINE-to-Excel

**Per:** DIRECTIVE 2026-07-09-H / P1c (config-over-code extraction)
**Purpose:** Every customer-specific value in ONE file = entire customization framework

---

## Quick Start (For Each New Customer)

1. **Copy the template:**
   ```bash
   cd /Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel
   cp customer_config.json.example customer_config.json
   ```

2. **Edit `customer_config.json` with customer's details:**
   - `business_name*` - Restaurant name in Thai/English/Chinese
   - `menu_items` - Complete menu with prices (for validation)
   - `templates` - Customize message templates if needed
   - `parsing_config` - Adjust requirements (e.g., make phone optional)

3. **Set environment variables** (credentials):
   ```bash
   export LINE_CHANNEL_SECRET="your_channel_secret"
   export LINE_CHANNEL_ACCESS_TOKEN="your_access_token"
   export GOOGLE_SHEET_ID="your_sheet_id"
   export GOOGLE_CREDENTIALS_PATH="path/to/credentials.json"
   ```

4. **Run:**
   ```bash
   uvicorn app:app --port 8001
   ```

---

## What Goes in Config vs Environment Variables

### `customer_config.json` (business logic, check into git)
**✅ Put here:**
- Restaurant name, menu items, prices
- Languages supported
- Message templates
- Parsing rules (require phone? require name?)
- Timezone, currency
- Demo mode settings

**Why:** These are business requirements that should be version-controlled with the code

### Environment variables (secrets, never commit)
**✅ Put here:**
- LINE Channel Secret
- LINE Channel Access Token
- Google Sheet ID
- Google Credentials JSON path
- Anthropic API key

**Why:** These are credentials that vary per deployment and should NEVER be in git

---

## Config Fields Reference

### Business Info
```json
{
  "business_name": "Som Tam Stand",
  "business_name_thai": "ร้านส้มตำ",
  "business_name_chinese": "木瓜沙拉摊"
}
```

### Menu Items (Critical for Validation)
```json
{
  "menu_items": [
    {
      "name_thai": "ผัดไทย",
      "name_chinese": "泰式炒面",
      "name_english": "Pad Thai",
      "price": 100
    }
  ]
}
```

**Purpose:** Parser can validate "ผัดไทย" or "Pad Thai" or "泰式炒面" all refer to same item.

**Menu setup tips:**
- Include ALL menu items (even drinks, sides)
- Prices help catch parsing errors (if Claude extracts ฿500 for ผัดไทย, you know it's wrong)
- Include common aliases (e.g., "炒饭" and "ข้าวผัด" both = Fried Rice)

### Templates (Message Customization)

```json
{
  "templates": {
    "daily_summary_thai": "📊 สรุปยอดวันนี้\n\n📦 ออเดอร์: {total_orders} รายการ\n💰 ยอดรวม: {total_revenue:,.0f} บาท\n\n🔥 เมนูขายดี:\n{top_items}"
  }
}
```

**Available placeholders:**
- `{total_orders}` - Number of orders today
- `{total_revenue}` - Total revenue (number)
- `{currency}` - Currency symbol from config
- `{top_items}` - Formatted list of best-sellers
- `{items}` - Order items list
- `{total}` - Order total

**When to customize:**
- Customer wants different emoji style
- Customer wants summary in only 1 language (not all 3)
- Customer wants extra info (e.g., delivery address)

### Parsing Config

```json
{
  "parsing_config": {
    "require_phone": true,
    "require_customer_name": true,
    "default_language": "thai",
    "auto_detect_language": true
  }
}
```

**`require_phone`:** `false` if customer accepts walk-ins without phone numbers
**`require_customer_name`:** `false` if customer OK with anonymous orders
**`default_language`:** Language for summary messages (if auto-detect fails)
**`auto_detect_language`:** `true` = detect from order message, `false` = always use default

### Demo Mode

```json
{
  "demo_mode": {
    "enabled": true,
    "sample_data_file": "sample_orders.json"
  }
}
```

**`enabled`:** `true` for testing without real LINE/Sheets, `false` for production
**`sample_data_file`:** Path to JSON file with test orders

**When to use demo mode:**
- Initial testing before customer provides credentials
- Demo pitches to new customers
- Development without internet connection

---

## Customization Examples

### Example 1: Street Food Cart (Thai only, no phone required)

```json
{
  "business_name": "Auntie Mai's Cart",
  "business_name_thai": "รถเข็นป้าใหม่",
  "supported_languages": ["thai"],
  "menu_items": [
    {"name_thai": "ส้มตำ", "price": 40},
    {"name_thai": "ไก่ย่าง", "price": 50}
  ],
  "parsing_config": {
    "require_phone": false,
    "require_customer_name": false
  }
}
```

### Example 2: Chinese Restaurant (Chinese + Thai, premium pricing)

```json
{
  "business_name": "Golden Dragon",
  "business_name_chinese": "金龙餐厅",
  "business_name_thai": "โกลเด้น ดราก้อน",
  "supported_languages": ["chinese", "thai"],
  "menu_items": [
    {"name_chinese": "北京烤鸭", "name_thai": "เป็ดปักกิ่ง", "price": 450},
    {"name_chinese": "麻婆豆腐", "name_thai": "เต้าหู้ราดซอสเผ็ด", "price": 180}
  ],
  "currency_symbol": "฿"
}
```

### Example 3: Tourist-Friendly Cafe (English primary)

```json
{
  "business_name": "Chiang Mai Cafe",
  "supported_languages": ["english", "thai"],
  "menu_items": [
    {"name_english": "Cappuccino", "name_thai": "คาปูชิโน่", "price": 80},
    {"name_english": "Banana Pancake", "name_thai": "แพนเค้กกล้วย", "price": 120}
  ],
  "parsing_config": {
    "default_language": "english"
  },
  "templates": {
    "daily_summary_english": "☕ Today's Summary\n\nOrders: {total_orders}\nRevenue: ฿{total_revenue:,.0f}\n\nBest Sellers:\n{top_items}"
  }
}
```

---

## Testing Your Config

**Before deploying to customer:**

1. **Menu validation test:**
   ```bash
   # Start server with your config
   uvicorn app:app --port 8001

   # Send test order via /parse endpoint
   curl -X POST http://localhost:8001/parse \
     -H "Content-Type: application/json" \
     -d '{"message": "ผัดไทย 2 จาน, ต้มยำกุ้ง 1 ถ้วย, รวม 350 บาท, โทร 081-234-5678"}'
   ```

2. **Check response:**
   - Are menu items recognized correctly?
   - Is total extracted accurately?
   - Is phone number parsed?

3. **Test edge cases:**
   - Order with typos ("ผัดไทก" instead of "ผัดไทย")
   - Order in multiple languages mixed
   - Order missing phone (if `require_phone: false`)

---

## Maintenance

**When customer adds new menu item:**
1. Edit `customer_config.json` → add to `menu_items`
2. Git commit: `git commit -m "Add [item name] to menu"`
3. Restart server (or use hot-reload if enabled)

**When customer changes pricing:**
1. Update `price` field in `menu_items`
2. No code changes needed

**When customer wants different summary format:**
1. Edit `templates.daily_summary_*`
2. Test with `/daily-summary` endpoint
3. Deploy

---

## Migration Path (For Existing Hardcoded Deployments)

**If you already deployed with hardcoded values:**

1. Extract current values into `customer_config.json`
2. Test locally to verify behavior unchanged
3. Deploy updated code + config together
4. Verify 24h of orders parse correctly
5. Mark as "config-driven deployment" in notes

**Rollback plan:** Keep old hardcoded version as `app_legacy.py` for 1 week, delete after.

---

## Summary: The Config-Over-Code Philosophy

**Before (hardcoded):**
- New customer = fork entire repo
- Menu change = code edit + deploy
- 3 customers = 3 separate repos

**After (config-driven):**
- New customer = copy config template, fill in blanks
- Menu change = edit JSON, restart
- 3 customers = 3 config files, 1 shared codebase

**Extraction happens after delivery #3** per P1e - don't build "shared platform" before proving it works 3 times.

---

**Next:** Use this config pattern for thai-chinese-translator demo (P1c continues)
