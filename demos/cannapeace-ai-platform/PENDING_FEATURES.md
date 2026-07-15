# Pending Features & Testing Tracker

**Last Updated:** 2026-07-15

---

## 🔴 NOT YET IMPLEMENTED

### High Priority:

#### 1. Age Gate System ⚠️ **LEGAL REQUIREMENT**
**Status:** Not implemented
**Urgency:** HIGH (legal compliance)
**Details:**
- Welcome → Language selection → **AGE GATE** → Nancy's voice greeting
- Two Quick Reply options:
  - ✅ "Yes, I'm over 20 years old"
  - ❌ "No, I'm under 20 years old"
- If YES → Proceed to Nancy's welcome
- If NO → Send terms link, educational message, block further interaction
- Should track in database (age_verified: true/false)

**Required:**
- Age gate message text (7 languages)
- Terms & Conditions Google Doc link
- Quick Reply buttons (Yes/No)
- Database field: age_verified
- Logic to block underage users from ordering

---

#### 2. Nancy Persona System 👧
**Status:** Not implemented
**Urgency:** HIGH (UX improvement)
**Details:**
- Create "Nancy" character:
  - Thai girl, 22 years old
  - Fresh graduate from Chulalongkorn University
  - Major: Pharmaceutical Sciences (Cannabis Therapeutics focus)
  - Multilingual: Thai, English, Chinese, Russian
  - Personality: Friendly, knowledgeable, helpful, professional
  - Voice: Sweet, young, energetic (already have voice files)
- Update all bot responses to sound like Nancy (less AI, more personal)
- Introduction message from Nancy (after age gate)

**Required:**
- Nancy's character profile document
- Update Claude prompts to speak as Nancy
- Nancy's introduction script (7 languages)
- Voice messages from Nancy (already partially done)

---

#### 3. Dynamic Language-Specific Voice Messages 🎙️
**Status:** Partially implemented (Chinese voice only)
**Urgency:** MEDIUM
**Details:**
- Currently: Same voice (Chinese) for all languages
- Need: 6 more voice files (Thai, English, Russian, Japanese, Korean, French)
- Nancy introduces herself in customer's language
- Scripts already written in VOICE_GREETING_SCRIPTS.md

**Required:**
- Generate 6 voice files using ElevenLabs
- Upload to Voices/Greetings/greeting_{language}.m4a
- Update voice endpoint to serve language-specific files
- Test each language

**Status Breakdown:**
- ✅ Chinese voice (CN4.m4a) - exists
- ❌ Thai voice - need to generate
- ❌ English voice - need to generate
- ❌ Russian voice - need to generate
- ❌ Japanese voice - need to generate
- ❌ Korean voice - need to generate
- ❌ French voice - need to generate

---

#### 4. Operator Notification System 🚨
**Status:** Designed but not implemented
**Urgency:** MEDIUM
**Details:**
- LINE Notify integration for operator alerts
- Automatic detection of customer issues
- Module Mode setup in LINE Official Account Manager

**Required:**
- Set up LINE Notify channel
- Get notification token
- Add detection code to handle_message()
- Configure Module Mode in LINE Official Account Manager
- Train operators on workflow

**Document:** OPERATOR_NOTIFICATION_SYSTEM.md (ready to implement)

---

### Medium Priority:

#### 5. Rich Menu (Persistent Bottom Navigation)
**Status:** Not implemented
**Urgency:** MEDIUM
**Details:**
- Persistent menu at bottom of LINE chat
- Buttons: Menu | Order | Language | Contact
- Always visible, no scrolling
- Better UX than Quick Reply (doesn't disappear)

**Required:**
- Design Rich Menu image (2500x843px)
- Upload via Messaging API
- Configure tap areas (4 buttons)
- Test on mobile

---

#### 6. Flex Messages (Beautiful Product Cards)
**Status:** Not implemented
**Urgency:** LOW
**Details:**
- Instagram-style strain cards
- Image, name, THC, type, effects, "Order" button
- More engaging than plain images
- Better product presentation

**Required:**
- Design Flex Message template (JSON)
- Integrate with strain info function
- Test across devices

---

#### 7. Carousel Messages (Swipeable Strain Browser)
**Status:** Not implemented
**Urgency:** LOW
**Details:**
- Show 3-4 strains in one message
- Swipe left/right to browse
- Alternative to Quick Reply buttons
- More visual, better for discovery

**Required:**
- Create carousel template
- Integrate with menu function
- Test on mobile

---

## 🟡 IMPLEMENTED BUT NOT TESTED

### 1. Follow Event (Auto-welcome when user adds bot)
**Status:** Deployed but not verified
**Deployed:** Commit db3c9dc
**Issue:** Don't know if it actually works when users add bot
**Testing Needed:**
- Delete user from Customers sheet
- Block/unblock bot in LINE
- Re-add bot via QR code
- Check if voice + welcome message sent automatically
- Check Railway logs for "New follower!" message

**Test Methods:**
- Use second LINE account (friend's phone)
- Check LINE webhook logs at https://manager.line.biz/
- Monitor Railway logs: `railway logs --tail 100 | grep follower`

---

### 2. Global Multilingual Welcome
**Status:** Deployed recently
**Deployed:** Commit e691031
**Testing Needed:**
- Test in each language (Thai, English, Chinese, Russian, Japanese, Korean, French)
- Verify compact language buttons appear
- Verify language selection works
- Check confirmation messages

**To Test:**
- Delete profile from Customers sheet
- Send first message
- Verify: "สวัสดี / Hello / 你好..." appears
- Tap each flag button
- Verify correct language confirmation

---

### 3. Quick Reply Persistent Browsing
**Status:** Deployed
**Deployed:** Commit 95b0b22
**Testing Needed:**
- Ask for menu
- Click strain button
- Verify Quick Reply buttons appear on strain info
- Click another strain
- Verify buttons persist throughout browsing

---

### 4. Multilingual Quick Reply Detection
**Status:** Deployed
**Deployed:** Commit 9b5dc97
**Testing Needed:**
- Switch to Chinese language
- Ask "菜单" (menu in Chinese)
- Verify Quick Reply buttons appear
- Repeat for Thai, Russian, Japanese, Korean, French

---

## 🟢 FULLY TESTED & WORKING

### 1. ✅ Quick Reply Buttons for Strain Menu
**Status:** Working
**Tested:** Yes
**Result:** Customers can click strain names to get info

### 2. ✅ Enhanced Strain Information
**Status:** Working
**Tested:** Yes
**Result:** Comprehensive info (flavor, effects, best for) displays correctly

### 3. ✅ Language Detection & Switching
**Status:** Working
**Tested:** Yes (text-based: "TH", "EN", "中文")
**Result:** Language switches correctly, confirmations work

### 4. ✅ Compact Language Buttons
**Status:** Working
**Deployed:** Commit c5a3c8e
**Result:** Just flag emojis, very compact

---

## 📊 FEATURE STATUS SUMMARY

| Feature | Status | Priority | Est. Time |
|---------|--------|----------|-----------|
| Age Gate System | ❌ Not implemented | 🔴 HIGH | 4 hours |
| Nancy Persona | ❌ Not implemented | 🔴 HIGH | 3 hours |
| Dynamic Voice (6 languages) | 🟡 Partial (1/7) | 🔴 HIGH | 4 hours |
| Operator Notifications | 🟡 Designed only | 🟠 MEDIUM | 4 hours |
| Follow Event | 🟡 Deployed, not tested | 🟠 MEDIUM | 1 hour |
| Multilingual Welcome | 🟡 Deployed, not tested | 🟠 MEDIUM | 1 hour |
| Quick Reply Browsing | ✅ Working | - | - |
| Enhanced Strain Info | ✅ Working | - | - |
| Compact Language Buttons | ✅ Working | - | - |
| Rich Menu | ❌ Not implemented | 🟡 LOW | 6 hours |
| Flex Messages | ❌ Not implemented | 🟡 LOW | 8 hours |
| Carousel Messages | ❌ Not implemented | 🟡 LOW | 4 hours |

---

## 🎯 RECOMMENDED IMPLEMENTATION ORDER

### This Week (HIGH PRIORITY):
1. **Age Gate System** (4 hours) - Legal requirement
2. **Nancy Persona** (3 hours) - Better UX
3. **Test Follow Event** (1 hour) - Verify it works
4. **Test Multilingual Welcome** (1 hour) - Verify all languages

### Next Week (MEDIUM PRIORITY):
1. **Generate 6 Voice Files** (4 hours) - Complete Nancy's voice
2. **Operator Notifications** (4 hours) - Enable human support
3. **Rich Menu** (6 hours) - Persistent navigation

### Later (LOW PRIORITY):
1. Flex Messages (8 hours)
2. Carousel Messages (4 hours)
3. VOOM Marketing (ongoing)

---

## 📝 TESTING CHECKLIST

### Before Launch:
- [ ] Age gate blocks underage users
- [ ] Nancy's introduction plays in correct language
- [ ] Follow Event sends auto-welcome
- [ ] All 7 languages work correctly
- [ ] Quick Reply buttons persistent
- [ ] Operator notifications working
- [ ] Voice messages play correctly
- [ ] Orders save to Google Sheets
- [ ] Customer profiles created correctly

### User Acceptance Testing:
- [ ] Test with real customers (5-10 people)
- [ ] Test all 7 languages
- [ ] Test on iOS devices
- [ ] Test on Android devices
- [ ] Test order flow end-to-end
- [ ] Test operator handoff
- [ ] Check response times

---

## 🐛 KNOWN ISSUES

### 1. Voice Language Mismatch
**Issue:** All languages get Chinese voice (CN4.m4a)
**Impact:** Thai users hear Chinese, English users hear Chinese, etc.
**Fix:** Generate 6 more voice files, update endpoint
**Priority:** HIGH

### 2. Follow Event Unverified
**Issue:** Don't know if auto-welcome actually triggers
**Impact:** Might not be working, users confused
**Fix:** Test with second account, check logs
**Priority:** MEDIUM

---

## 💡 FUTURE IDEAS (NOT PRIORITIZED YET)

- LIFF checkout page (embedded web app)
- Beacon integration (in-store)
- Account linking (LINE Login)
- Payment integration
- Delivery tracking
- Loyalty program
- Referral system
- Customer reviews
- Product recommendations (AI-based)
- Inventory management
- Analytics dashboard

---

**Next Update:** After implementing age gate + Nancy persona
