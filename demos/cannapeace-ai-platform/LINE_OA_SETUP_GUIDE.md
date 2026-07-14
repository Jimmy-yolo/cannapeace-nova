# LINE Official Account Setup Guide — Customer Zero (CannaPeace)

**Purpose:** Create LINE Official Account for Restaurant LINE-to-Excel bot
**Customer:** CannaPeace (Customer Zero / Internal Test)
**Date:** 2026-07-10

---

## Part 1: Create LINE Official Account (Jimmy Does This)

### Step 1: Access LINE Official Account Manager (5 minutes)

**URL:** https://manager.line.biz/

**Actions:**
1. Open https://manager.line.biz/ in browser
2. Click "Create a LINE Official Account" (or "Log In" if you have existing accounts)
3. Log in with your LINE account
   - **If you don't have LINE:** Download LINE app first → Create account → Then return to manager.line.biz

**Expected result:** You're at the LINE Official Account Manager dashboard

---

### Step 2: Create New Official Account (10 minutes)

**Click "Create" button**

**Fill in required fields:**

1. **Account Name (Display Name):**
   ```
   CannaPeace Orders
   ```
   *(This is what customers see)*

2. **Account Type:**
   - Select: **Food & Beverage → Restaurant / Cafe**

3. **Company/Owner Name:**
   ```
   CannaPeace
   ```

4. **Industry:**
   - Select: **Food & Beverage**

5. **Sub-industry:**
   - Select: **Restaurant**

6. **Region:**
   - Select your country (e.g., Thailand)

7. **Email Address:**
   - Use your email (for notifications)

8. **Terms of Service:**
   - Check "I agree to the LINE Official Account Terms of Use"
   - Click "Create"

**Expected result:** Account created, you see the Dashboard

---

### Step 3: Configure Account Settings (5 minutes)

**In the Dashboard, go to Settings → Response settings:**

1. **Greeting message:** ON
   - Edit message:
   ```
   👋 สวัสดีค่ะ! ยินดีต้อนรับสู่ CannaPeace

   ส่งข้อความสั่งอาหารได้เลยค่ะ
   ตัวอย่าง:
   ผัดไทย 2 จาน
   ต้มยำกุ้ง 1 ถ้วย
   รวม 350 บาท
   ชื่อ: คุณสมชาย
   โทร: 081-234-5678
   ```

2. **Auto-reply messages:** OFF
   *(We'll use webhook instead)*

3. **Webhook:** OFF *(for now, will enable after deployment)*

4. **Save changes**

---

### Step 4: Get LINE Credentials (10 minutes)

**These are the 2 credentials needed for the bot:**

#### Credential 1: Channel Secret

1. Go to **Settings** → **Messaging API**
2. Scroll to **Channel secret**
3. Click "Issue" or view existing secret
4. **Copy this value** → Save securely

**Format:** Looks like `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`

---

#### Credential 2: Channel Access Token

1. Same page: **Messaging API** tab
2. Scroll to **Channel access token**
3. Click "Issue" button
4. **Copy the long token** → Save securely

**Format:** Looks like `abc123def456...` (very long, ~170 characters)

**⚠️ IMPORTANT:**
- Never share these publicly
- Store in config-private.json (gitignored)
- If leaked, regenerate immediately

---

### Step 5: Note Your Bot's Basic ID (2 minutes)

1. Go to **Settings** → **Account settings**
2. Find **Basic ID** or **LINE ID**
   - Format: `@xxx-yyyyy`
3. **Save this** - you'll add the bot to your LINE app using this ID

**Example:** `@123abcde`

---

## Part 2: Set Up Google Sheets (Jimmy Does This)

### Step 6: Create Google Sheet (5 minutes)

1. Go to: https://sheets.google.com
2. Click "+ Blank" to create new sheet
3. **Rename sheet:** "CannaPeace Orders"
4. Add headers in Row 1:
   ```
   A1: Timestamp
   B1: Customer Name
   C1: Phone
   D1: Items
   E1: Total (THB)
   F1: Order Text
   ```

5. **Copy the Sheet ID** from URL:
   ```
   https://docs.google.com/spreadsheets/d/[THIS_IS_THE_SHEET_ID]/edit
   ```

**Save the Sheet ID** - needed for config

---

### Step 7: Create Google Service Account (15 minutes)

**URL:** https://console.cloud.google.com/

1. **Create project:**
   - Click "Select a project" → "New Project"
   - Project name: `cannapeace-orders`
   - Click "Create"

2. **Enable Google Sheets API:**
   - Search for "Google Sheets API" in top search bar
   - Click "Google Sheets API"
   - Click "Enable"

3. **Create Service Account:**
   - Go to: "IAM & Admin" → "Service Accounts"
   - Click "+ CREATE SERVICE ACCOUNT"
   - Service account name: `cannapeace-bot`
   - Description: "Restaurant order bot"
   - Click "CREATE AND CONTINUE"
   - Skip roles (click "CONTINUE")
   - Click "DONE"

4. **Create Key (JSON):**
   - Click on the service account you just created
   - Go to "KEYS" tab
   - Click "ADD KEY" → "Create new key"
   - Select "JSON"
   - Click "CREATE"
   - **File downloads automatically** → Save as `credentials.json`

5. **Get Service Account Email:**
   - Copy the email shown (format: `cannapeace-bot@cannapeace-orders.iam.gserviceaccount.com`)

**Expected result:** You have `credentials.json` file downloaded

---

### Step 8: Share Sheet with Service Account (2 minutes)

1. Open your Google Sheet "CannaPeace Orders"
2. Click "Share" button (top right)
3. **Paste the service account email:**
   ```
   cannapeace-bot@cannapeace-orders.iam.gserviceaccount.com
   ```
4. Permission: **Editor**
5. **Uncheck** "Notify people"
6. Click "Share"

**Expected result:** Service account has edit access to sheet

---

## Part 3: Handoff to Claude Code

### Step 9: Provide Credentials to Claude Code

**Create file:** `credentials-for-claude.txt` (local only, don't commit)

**Format:**
```
=== LINE CREDENTIALS ===
Channel Secret: [paste here]
Channel Access Token: [paste here]
Bot Basic ID: @[paste here]

=== GOOGLE CREDENTIALS ===
Sheet ID: [paste here]
Service Account Email: [paste here]
credentials.json location: [full path, e.g., /Users/jimmy/Downloads/credentials.json]

=== CUSTOMER INFO ===
Business Name: CannaPeace
Business Name Thai: แคนนาพีซ
Business Name Chinese: 大麻和平
Supported Languages: thai, chinese, english

=== SAMPLE MENU (for config) ===
1. ผัดไทย / 泰式炒面 / Pad Thai - 100 THB
2. ต้มยำกุ้ง / 冬阴功汤 / Tom Yum Goong - 150 THB
3. ข้าวผัด / 炒饭 / Fried Rice - 80 THB
4. แกงเขียวหวาน / 绿咖喱 / Green Curry - 120 THB
5. ข้าวเหนียวมะม่วง / 芒果糯米饭 / Mango Sticky Rice - 80 THB
```

**Tell Claude Code:**
> "Ready for Customer Zero deployment. Credentials are in credentials-for-claude.txt. Use CannaPeace as first customer per INSTALL_CHECKLIST.md and fill in FRICTION_LOG.md as you go."

---

## Part 4: After Deployment (Claude Does This)

### Step 10: Enable Webhook in LINE

**After Railway deployment completes:**

1. Go back to: https://manager.line.biz/
2. Select "CannaPeace Orders" account
3. Go to **Settings** → **Messaging API**
4. **Webhook URL:**
   ```
   https://[your-railway-url]/webhook
   ```
   *(Claude will provide this URL after deployment)*

5. **Use webhook:** Toggle to ON
6. Click "Verify" button next to webhook URL
   - Should show: "Success" ✅

7. **Auto-reply messages:** Make sure this is OFF

**Expected result:** Webhook connected, bot ready to receive messages

---

### Step 11: Test with LINE App (Jimmy Does This)

1. Open LINE app on your phone
2. Add the bot:
   - Tap "Home" → "Add friends" → "Search"
   - Enter the Basic ID: `@xxx-yyyyy`
   - Add as friend

3. Send test order:
   ```
   ผัดไทย 2 จาน
   ต้มยำกุ้ง 1 ถ้วย
   รวม 350 บาท
   คุณจิมมี่
   โทร 081-234-5678
   ```

4. **Check:**
   - Bot responds with confirmation ✅
   - Order appears in Google Sheet ✅

**Expected result:** Order flows through: LINE → Bot → Sheet

---

## Summary: What Jimmy Needs to Do

**Total time:** ~45 minutes

1. ✅ Create LINE Official Account (Steps 1-3)
2. ✅ Get LINE credentials: Channel Secret + Access Token (Step 4)
3. ✅ Create Google Sheet (Step 6)
4. ✅ Create Google Service Account + credentials.json (Step 7)
5. ✅ Share sheet with service account (Step 8)
6. ✅ Provide all credentials to Claude Code (Step 9)
7. ⏸ Wait for Claude Code to deploy
8. ✅ Enable webhook in LINE (Step 10)
9. ✅ Test with LINE app (Step 11)

---

## Troubleshooting

### Issue: Can't log in to LINE Official Account Manager
**Fix:** Make sure you have LINE app installed and logged in first

### Issue: "Channel Secret" section is empty
**Fix:** Click "Issue" button to generate new secret

### Issue: 403 error when bot tries to write to Sheet
**Fix:** Verify sheet is shared with service account email (check spelling)

### Issue: Webhook verification fails
**Fix:**
1. Check Railway deployment is running
2. Check webhook URL is exactly: `https://[url]/webhook` (no trailing slash)
3. Check "Use webhook" is toggled ON

### Issue: Bot receives message but doesn't respond
**Fix:**
1. Check Railway logs for errors
2. Verify credentials in Railway env vars
3. Check "Auto-reply" is OFF in LINE settings

---

## Next Steps After Customer Zero

**After 3 days of successful operation:**

1. Complete FRICTION_LOG.md with actual friction points
2. Rank top-5 fixes
3. Update INSTALL_CHECKLIST.md with actual timings
4. Apply fixes before approaching real customer #1
5. Customer #1 gets refined, tested install process

**Success criteria (Acceptance Test):**
- ✅ 3 consecutive days of real orders
- ✅ ≥90% parse accuracy
- ✅ Zero bot downtime
- ✅ Daily summary works
- ✅ Jimmy can independently restart if needed

---

## Customer Zero Advantages

**Why CannaPeace is perfect for Customer Zero:**
1. **Instant feedback** - You're both developer and customer
2. **Safe testing** - Internal project, low risk
3. **Real scenarios** - Can simulate various order formats
4. **Documentation** - Perfect for filling FRICTION_LOG
5. **Iteration speed** - Can fix issues immediately

**Use CannaPeace to test:**
- Thai/Chinese/English orders
- Missing phone numbers
- Typos in menu items
- Mixed language orders
- Edge cases (very large orders, special characters)

---

**Ready to start?** Follow Steps 1-9, then tell Claude Code: "Credentials ready for Customer Zero deployment"
