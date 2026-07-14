# Language System Bug - Session Handoff

**Date:** 2026-07-14
**Issue:** Language switch prompt keeps repeating, won't proceed to normal conversation

---

## Bug Description

Customer reports: Bot keeps sending language switch prompt on every message instead of having normal conversation.

**Expected behavior:**
1. First message → Send greeting with language options
2. Customer sends regular message → Normal conversation (no greeting)
3. Customer sends 🇬🇧 → Switch language, confirm, continue

**Actual behavior:**
- Bot sends greeting/language prompt on EVERY message (stuck in loop)

---

## Likely Causes

### 1. First Message Detection Bug
**Location:** `app.py` line ~836

```python
is_first_message = not profile or profile.get('total_messages', 0) == 0
if is_first_message:
    greeting = get_greeting_message(current_language)
    # ... send greeting
    return
```

**Problem:** `total_messages` field doesn't exist in customer profile dict!

**Proof:** Check `get_customer_profile()` function - it doesn't include `total_messages` in the returned dict.

### 2. Language Preference Not Saved
**Check:** Customers sheet column F - is language being saved?

### 3. Profile Not Being Found
**Check:** Is `get_customer_profile()` returning None every time?

---

## How to Debug (Next Session)

### Step 1: Check Railway Logs
```bash
cd /Users/jimmy/CannaPeace/products/nova/demos/cannapeace-ai-platform
railway logs | grep "first_message\|language\|profile"
```

Look for:
- "✅ Created new customer profile" (should only happen once)
- "✅ Updated language to..." (when flag sent)
- Any errors in get_customer_profile()

### Step 2: Check Google Sheet
Open: https://docs.google.com/spreadsheets/d/1Rz1DbllW-0ezJKM4Qsf58D8WAMPxuP5HOXzAbVgMQIY/edit

**Customers sheet:**
- Is there a row for your user?
- Is column F (Language_Preference) populated?
- Is the profile being created/updated?

### Step 3: Check Messages Sheet
- Are messages being logged?
- Is the same user_id appearing in multiple rows?

---

## Fix Options

### Fix 1: Remove total_messages Check (Quick)
```python
# BEFORE (BROKEN):
is_first_message = not profile or profile.get('total_messages', 0) == 0

# AFTER (FIX):
is_first_message = not profile  # Only check if profile exists
```

### Fix 2: Add total_messages to Profile (Better)
1. Add `Total_Messages` column to Customers sheet
2. Update `get_customer_profile()` to return total_messages
3. Increment on every message

### Fix 3: Check Messages Sheet Instead (Best)
```python
# Count messages from Messages sheet
def is_first_message_for_user(user_id):
    result = sheets_service.spreadsheets().values().get(
        spreadsheetId=GOOGLE_SHEET_ID,
        range='Messages!B:B'  # LINE_User_ID column
    ).execute()

    user_messages = [row for row in result.get('values', []) if row and row[0] == user_id]
    return len(user_messages) <= 1  # 1 because we already logged current message
```

---

## Recommended Fix (Fast)

**File:** `app.py` line ~836

**Change:**
```python
# OLD (BROKEN):
is_first_message = not profile or profile.get('total_messages', 0) == 0
if is_first_message:
    greeting = get_greeting_message(current_language)
    if line_bot_api:
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=greeting))
    return

# NEW (FIXED):
# Only send greeting if profile was JUST created (first contact ever)
# Profile will exist after first message, so we skip greeting on subsequent messages
# Language switching has its own return path above
# So this is unreachable on normal messages
# REMOVE THIS ENTIRE BLOCK - greeting only needed on very first contact,
# and that's already handled by profile creation
```

**Better approach:** Just remove the greeting block entirely, or only show it on absolute first contact when profile is created.

---

## Testing After Fix

1. **Fresh user test:**
   - Delete your user from Customers sheet
   - Send "hi" → Should get greeting with language options
   - Send "show menu" → Should get menu (NO greeting again)

2. **Language switch test:**
   - Send 🇬🇧 → Should get confirmation in English
   - Send "hi" → Should respond in English (NO language prompt again)

3. **Existing user test:**
   - Send message → Should respond normally (NO greeting)

---

## Current Code State

**Commits:**
- `5b71f88` - Added multilingual support (HAS THE BUG)
- `15c77d5` - Smart phone/name extraction
- `a0cb437` - Manual CRM setup endpoint

**Deployed:** Yes (Railway auto-deployed the buggy code)

**Sheets Created:** Yes (5 sheets exist with proper headers)

**Working Features:**
- ✅ CRM sheets auto-creation
- ✅ Customer profile creation
- ✅ Message logging
- ✅ Phone/name extraction
- ❌ Language switching (BROKEN - this bug)
- ❌ Greeting message (BROKEN - loops)

---

## Quick Commands (Resume Session)

```bash
# Check logs
cd /Users/jimmy/CannaPeace/products/nova/demos/cannapeace-ai-platform
railway logs | tail -100

# Edit the fix
code app.py  # Go to line ~836

# Test syntax
python3 -m py_compile app.py

# Deploy
git add app.py
git commit -m "fix: Remove greeting loop, fix first message detection"
git push
```

---

## Summary for Next Session

**Problem:** Greeting/language prompt loops on every message

**Root cause:** `profile.get('total_messages', 0)` always returns 0 because `total_messages` doesn't exist in profile dict

**Fix:** Remove or simplify first message detection logic

**Time to fix:** ~5 minutes (change 1 line, test, deploy)

**Priority:** HIGH - blocks all conversations

---

Ready to resume after compact! 🚀
