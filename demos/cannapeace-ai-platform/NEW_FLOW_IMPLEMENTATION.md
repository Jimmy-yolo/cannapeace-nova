# New Onboarding Flow Implementation Plan

**Date:** 2026-07-15
**Status:** Ready to implement
**Priority:** HIGH (Legal compliance + UX improvement)

---

## 🎯 NEW FLOW DESIGN

### Current Flow (OLD):
```
1. User adds bot / sends first message
2. Bot: Global welcome + Language Quick Reply buttons
3. User selects language (e.g., 🇹🇭)
4. Bot: Confirmation + ready to chat
❌ No age verification
❌ Generic AI tone
❌ No personalization
```

### New Flow (IMPROVED):
```
1. User adds bot / sends first message
2. Bot: Global welcome ("สวัสดี / Hello / 你好...") + Language Quick Reply
3. User selects language (e.g., 🇹🇭)
4. Bot: Age Gate message + Quick Reply ([✅ Yes, I'm 20+] [❌ No, I'm under 20])
5a. IF YES → Bot: Nancy's voice greeting + short welcome text
5b. IF NO → Bot: Educational message + Terms link + BLOCK from ordering
6. User ready to browse/order
```

---

## 📋 COMPONENTS CREATED (READY)

### ✅ 1. Nancy Persona Profile
**File:** `NANCY_PERSONA.md`

**Character:**
- Name: Nancy Siriwat (นันซี่ ศิริวัฒน์)
- Age: 22 years old
- Education: Chul Pharmaceutical Sciences (Cannabis Therapeutics)
- Personality: Friendly, knowledgeable, fresh graduate energy
- Languages: Thai native, English fluent, Chinese conversational

**Voice:**
- Sweet, young, energetic (already have voice files)
- Introduces herself in customer's language
- Short text to accompany voice (doesn't override voice message space)

---

### ✅ 2. Age Gate System
**Function:** `create_age_gate_quick_reply()`
**Quick Reply Buttons:**
- ✅ "Yes, I'm 20+" → Proceed to Nancy's welcome
- ❌ "No, I'm under 20" → Educational message + block

**Age Gate Messages:** All 7 languages ready
- Thai: "🔞 ยืนยันอายุ / Age Verification..."
- English, Chinese, Russian, Japanese, Korean, French

**Requirements Listed:**
- Must be 20+ (Thai law)
- Not for pregnant/breastfeeding women
- Use responsibly
- Link to Terms & Conditions (Google Doc)

---

### ✅ 3. Nancy's Welcome Messages
**Function:** `get_nancy_welcome(language)`

**Short text (accompanies voice):**
- Thai: "ฉันชื่อ Nancy ค่ะ - เพิ่งจบ Pharmaceutical Sciences จาก จุฬาฯ มา! 🎓..."
- English: "I'm Nancy - just graduated from Chula..."
- All 7 languages

**Design:**
- SHORT (3 lines max) - doesn't override voice message space
- Personal, not AI-like
- Mentions Nancy's background (Chula, Pharmaceutical Sciences)
- Call to action: "Type 'menu' to see strains!"

---

## 🔨 IMPLEMENTATION STEPS

### Step 1: Update Postback Handler ✅ (Code ready, needs integration)

Current location: `app.py` line ~1515

**Add handling for:**
1. `language:{code}` → Send age gate
2. `age_verified:yes` → Send Nancy's welcome
3. `age_verified:no` → Send educational message + block

**Pseudo-code:**
```python
def handle_postback(event):
    # ... existing code ...

    # Handle language selection
    if postback_data.startswith("language:"):
        language_code = ...
        update_customer_language(user_id, language_code)

        # NEW: Instead of just confirmation, send age gate
        age_gate_msg = get_age_gate_message(language_code)
        text_message = TextSendMessage(text=age_gate_msg)
        text_message.quick_reply = create_age_gate_quick_reply()
        line_bot_api.reply_message(event.reply_token, text_message)
        return

    # NEW: Handle age verification
    if postback_data.startswith("age_verified:"):
        response = postback_data.split(":")[1]  # "yes" or "no"
        profile = get_customer_profile(user_id)
        language = profile.get('language_preference', 'thai')

        if response == "yes":
            # Update profile: age_verified = True
            update_customer_age_verified(user_id, True)

            # Send Nancy's voice + welcome
            messages = []

            # Voice message from Nancy
            base_url = ...
            voice_url = f"{base_url}/greeting-voice/{language}"  # Language-specific!
            messages.append(AudioSendMessage(...))

            # Short text welcome from Nancy
            nancy_text = get_nancy_welcome(language)
            messages.append(TextSendMessage(text=nancy_text))

            line_bot_api.reply_message(event.reply_token, messages)

        else:  # response == "no" (underage)
            # Update profile: age_verified = False
            update_customer_age_verified(user_id, False)

            # Send educational message
            underage_msg = get_underage_message(language)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(text=underage_msg))

        return
```

---

### Step 2: Add Database Field for Age Verification

**Google Sheets "Customers" table:**
- Add column: `Age_Verified` (Boolean or Text: "Yes"/"No"/"Pending")

**Functions needed:**
```python
def update_customer_age_verified(user_id, verified):
    """Update age_verified field in Customers sheet"""
    # Implementation similar to update_customer_language()
    pass

def get_underage_message(language):
    """Get message for underage users"""
    messages = {
        'thai': """ขออภัยค่ะ 😊

ตามกฎหมายไทย เราสามารถให้บริการเฉพาะผู้ที่มีอายุ 20 ปีขึ้นไปเท่านั้นค่ะ

📚 **แต่คุณสามารถเรียนรู้เพิ่มเติมได้ที่:**
• ข้อมูลเกี่ยวกับกัญชาในประเทศไทย
• ประโยชน์ทางการแพทย์
• การใช้อย่างปลอดภัย

📄 อ่านเพิ่มเติม: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

หวังว่าจะได้พบคุณอีกครั้งเมื่อคุณมีอายุครบ 20 ปีค่ะ! 🌿""",

        'english': """Sorry! 😊

Under Thai law, we can only serve customers aged 20 and above.

📚 **But you can still learn more about:**
• Cannabis information in Thailand
• Medical benefits
• Safe usage

📄 Read more: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

Hope to see you when you turn 20! 🌿""",

        # ... other languages
    }
    return messages.get(language, messages['thai'])
```

---

### Step 3: Block Underage Users from Ordering

**In `handle_message()` before Claude processing:**
```python
# Check age verification
profile = get_customer_profile(user_id)
age_verified = profile.get('age_verified', None)

if age_verified == False:  # Explicitly marked as underage
    # Block from using the bot
    blocked_msg = get_underage_blocked_message(language)
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=blocked_msg))
    return  # Don't process further

if age_verified is None:  # Haven't verified yet
    # Shouldn't happen (flow ensures verification), but handle it
    age_gate_msg = get_age_gate_message(language)
    text_message = TextSendMessage(text=age_gate_msg)
    text_message.quick_reply = create_age_gate_quick_reply()
    line_bot_api.reply_message(event.reply_token, text_message)
    return
```

---

### Step 4: Update Claude Prompt to be "Nancy"

**In `handle_message()` where Claude prompt is built:**
```python
# Change from generic AI to Nancy persona
prompt = f"""You are Nancy Siriwat, a 22-year-old Thai girl who just graduated from Chulalongkorn University with a degree in Pharmaceutical Sciences, specializing in Cannabis Therapeutics. You work at CannaPeace in Bangkok.

PERSONALITY:
- Friendly, warm, knowledgeable (fresh graduate energy!)
- Multilingual: Thai native, English fluent, Chinese conversational
- Use 😊 and 🌿 emojis naturally (not excessively)
- Educational but not preachy
- Safety-conscious (always remind "start low, go slow")

TONE ({lang_instruction}):
- In Thai: Use ค่ะ, warm and polite
- In English: Casual but professional ("Hey!" not "Dear Customer")
- Make it conversational, like chatting with a friend who knows pharmacy

YOUR KNOWLEDGE:
- Deep understanding of strains, terpenes, cannabinoids
- Can explain complex topics simply ("So basically...")
- Share fun facts from pharmacy school ("Did you know...?")

ALWAYS:
- Be helpful and educational
- Remind about responsible use
- Never diagnose medical conditions (refer to doctors)
- Never be pushy about sales

CONVERSATION HISTORY:
{history_text}

CUSTOMER'S MESSAGE:
{message_text}

YOUR PRODUCTS:
{products_info}

RESPOND AS NANCY (warm, friendly, knowledgeable):"""
```

---

## 📊 NEW USER EXPERIENCE

### Example Flow (Thai user):

**Step 1: First Contact**
```
USER: *Adds bot or sends "hi"*

BOT: (Voice message plays)
BOT: "สวัสดี / Hello / 你好 / Привет / こんにちは / 안녕하세요 / Bonjour

🌿 Welcome to CannaPeace!

I'm your AI chatbot assistant, available 24/7...

💬 Choose your language:
👇 Tap a flag below!"

[🇹🇭] [🇬🇧] [🇨🇳] [🇷🇺] [🇯🇵] [🇰🇷] [🇫🇷]
```

**Step 2: Language Selection**
```
USER: *Taps [🇹🇭]*
Chat shows: "ไทย"

BOT: "🔞 ยืนยันอายุ / Age Verification

ตามกฎหมายไทย กัญชาสามารถจำหน่ายได้เฉพาะบุคคลที่มีอายุ 20 ปีขึ้นไปเท่านั้น

CannaPeace จำหน่ายกัญชาเพื่อ:
• การพักผ่อน (Recreational use)
• การบำบัดแบบดั้งเดิม (Traditional therapy)
• การใช้งานส่วนบุคคล (Personal use)

⚠️ ข้อกำหนด:
• ห้ามขายให้ผู้ที่อายุต่ำกว่า 20 ปี
• ห้ามขายให้สตรีมีครรภ์หรือให้นมบุตร
• ใช้อย่างมีความรับผิดชอบ

📄 อ่านข้อกำหนดและเงื่อนไขฉบับเต็ม: [Terms & Conditions]

คุณมีอายุ 20 ปีขึ้นไปหรือไม่?"

[✅ Yes, I'm 20+] [❌ No, I'm under 20]
```

**Step 3a: Age Verified (Yes)**
```
USER: *Taps [✅ Yes, I'm 20+]*
Chat shows: "Yes, I'm over 20 years old"

BOT: (Nancy's voice message plays in Thai)
"สวัสดีค่ะ! ฉันชื่อ Nancy
ยินดีต้อนรับสู่ CannaPeace..."

BOT: "ฉันชื่อ Nancy ค่ะ - เพิ่งจบ Pharmaceutical Sciences จาก จุฬาฯ มา! 🎓

มีอะไรให้ช่วยไหมคะวันนี้? 😊
พิมพ์ "ดูเมนู" เพื่อดูสายพันธุ์กัญชาทั้งหมด!"

USER: *Now free to chat, browse menu, order*
```

**Step 3b: Underage (No)**
```
USER: *Taps [❌ No, I'm under 20]*
Chat shows: "No, I'm under 20 years old"

BOT: "ขออภัยค่ะ 😊

ตามกฎหมายไทย เราสามารถให้บริการเฉพาะผู้ที่มีอายุ 20 ปีขึ้นไปเท่านั้นค่ะ

📚 แต่คุณสามารถเรียนรู้เพิ่มเติมได้ที่:
• ข้อมูลเกี่ยวกับกัญชาในประเทศไทย
• ประโยชน์ทางการแพทย์
• การใช้อย่างปลอดภัย

📄 อ่านเพิ่มเติม: [Terms & Conditions]

หวังว่าจะได้พบคุณอีกครั้งเมื่อคุณมีอายุครบ 20 ปีค่ะ! 🌿"

BOT: *Blocks further interaction (any message → "You must be 20+")*
```

---

## ✅ READY TO DEPLOY

### Files Created:
- ✅ `PENDING_FEATURES.md` - Complete feature tracker
- ✅ `NANCY_PERSONA.md` - Nancy character profile
- ✅ `STAFF_MANAGEMENT_GUIDE.md` - Operator team setup
- ✅ `NEW_FLOW_IMPLEMENTATION.md` - This file (implementation plan)

### Code Ready (in `app.py`):
- ✅ `create_age_gate_quick_reply()` - Age gate buttons
- ✅ `get_age_gate_message(language)` - Age gate text (7 languages)
- ✅ `get_nancy_welcome(language)` - Nancy's short welcome (7 languages)

### Still Needed (Next Session):
1. Update postback handler to implement new flow
2. Add `age_verified` column to Customers sheet
3. Implement `update_customer_age_verified()` function
4. Implement underage blocking logic
5. Update Claude prompt to be "Nancy"
6. Test complete flow end-to-end
7. Generate Nancy's voice files for 6 languages (Thai, English, Russian, Japanese, Korean, French)

---

## 🎯 ESTIMATED TIME

| Task | Time | Priority |
|------|------|----------|
| Update postback handler | 1 hour | HIGH |
| Add database field | 30 min | HIGH |
| Implement blocking logic | 30 min | HIGH |
| Update Claude prompt to Nancy | 30 min | HIGH |
| Test end-to-end | 1 hour | HIGH |
| Generate 6 voice files | 2 hours | MEDIUM |

**Total:** ~5-6 hours

---

## 💡 BENEFITS OF NEW FLOW

### Legal Compliance:
- ✅ Age verification required by Thai law
- ✅ Clear terms & conditions
- ✅ Underage users blocked from ordering
- ✅ Audit trail (age_verified in database)

### Better UX:
- ✅ Personal connection (Nancy, not generic AI)
- ✅ Trustworthy (fresh pharmacy graduate)
- ✅ Educational (cannabis expertise)
- ✅ Warm welcome in customer's language
- ✅ Voice + text (engaging onboarding)

### Business Value:
- ✅ Legal protection
- ✅ Brand differentiation (Nancy persona)
- ✅ Higher trust (education background)
- ✅ Better conversion (personal touch)
- ✅ Multilingual support (7 languages)

---

**Ready to implement in next session!** 🚀
