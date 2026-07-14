# Follow Event System - Session Handoff

**Date:** 2026-07-15
**Status:** Deployed but needs testing & voice language fix

---

## Current State

### What's Deployed (Commit: db3c9dc)
1. ✅ Follow Event handler (`handle_follow` function)
2. ✅ Proactive welcome message in 7 languages
3. ✅ Voice + text greeting on Follow Event
4. ✅ Customer profile auto-creation
5. ✅ Attribution capture on follow

### What Needs Fixing

#### 🔴 ISSUE 1: Voice Language Mismatch
**Problem:** Currently using Chinese voice (CN4.m4a) for ALL languages
- File: `greeting_voice.m4a` is hardcoded
- Should send Thai voice to Thai users, English to English users, etc.

**Solution Needed:**
- Have 7 voice files: `greeting_thai.m4a`, `greeting_english.m4a`, etc.
- Dynamically select voice based on customer's language preference
- Code location: `app.py` lines 1209-1217 (voice URL generation)

#### 🔴 ISSUE 2: Follow Event Not Tested
**Problem:** Don't know if auto-welcome actually works
- Unfriend/refriend is tedious to test
- Not sure if it's working or status issue

**Need:**
- Check Railway logs for "New follower!" message
- Better testing method
- Verify FollowEvent is registered correctly

---

## Testing Follow Event (Better Methods)

### Method 1: Check Railway Logs (EASIEST)
```bash
cd /Users/jimmy/CannaPeace/products/nova/demos/cannapeace-ai-platform
railway logs --tail 50 | grep -i "follow\|follower\|welcome"
```

Look for:
- "🎉 New follower! User ID: ..."
- "✅ Sent proactive welcome to new follower: ..."

If you see these → It's working!
If NOT → Follow event handler not triggering

### Method 2: Use Another LINE Account
- Use friend's account to add bot
- Or create test LINE account
- Add bot → Should get instant welcome

### Method 3: Check LINE Bot Console
1. Go to: https://manager.line.biz/
2. Find CannaPeace bot
3. Settings → Messaging API
4. Check webhook logs
5. Look for "follow" events

### Method 4: Test with Unfollow First
1. Open bot chat → Settings → Block
2. Settings → Delete chat
3. Re-add bot via QR code
4. Should trigger Follow Event

---

## Code Locations

### Follow Event Handler
**File:** `app.py` lines 1180-1241
```python
def handle_follow(event):
    """Handle when user adds bot as friend (Follow Event)"""
    # Creates profile
    # Sends voice + welcome message
```

### Event Registration
**File:** `app.py` line 1245
```python
handler.add(FollowEvent)(handle_follow)
```

### Welcome Messages (7 languages)
**File:** `app.py` lines 538-671
```python
def get_welcome_message(language: str = 'thai'):
    # Returns proactive welcome emphasizing it's a chatbot
```

---

## Voice Language Fix (To Do After Compact)

### Step 1: Generate All 7 Voice Greetings
Using ElevenLabs:
- Thai: "สวัสดีค่ะ! ยินดีต้อนรับสู่แคนนาพีซ..."
- English: "Hey there! Welcome to CannaPeace!..."
- Chinese: "嗨！欢迎来到CannaPeace！..." (already have this)
- Russian: "Привет! Добро пожаловать в CannaPeace!..."
- Japanese: "こんにちは！CannaPeaceへようこそ！..."
- Korean: "안녕하세요! CannaPeace에 오신 것을 환영합니다!..."
- French: "Salut! Bienvenue à CannaPeace!..."

Scripts are in: `VOICE_GREETING_SCRIPTS.md`

### Step 2: Upload Voice Files
Save as:
```
Voices/Greetings/greeting_thai.m4a
Voices/Greetings/greeting_english.m4a
Voices/Greetings/greeting_chinese.m4a
Voices/Greetings/greeting_russian.m4a
Voices/Greetings/greeting_japanese.m4a
Voices/Greetings/greeting_korean.m4a
Voices/Greetings/greeting_french.m4a
```

### Step 3: Update Code to Use Dynamic Voice
Change in 2 places:

**A) Follow Event Handler (line ~1213)**
```python
# CURRENT (WRONG - hardcoded):
voice_url = f"{base_url}/greeting-voice"

# CHANGE TO (CORRECT - dynamic):
voice_url = f"{base_url}/greeting-voice/{current_language}"
```

**B) First Message Handler (line ~879)**
```python
# Same change
voice_url = f"{base_url}/greeting-voice/{current_language}"
```

### Step 4: Update Voice Endpoint
Change endpoint to accept language parameter:

```python
# CURRENT:
@app.get("/greeting-voice")
async def serve_greeting_voice():
    voice_file = Path("greeting_voice.m4a")
    # ...

# CHANGE TO:
@app.get("/greeting-voice/{language}")
async def serve_greeting_voice(language: str = "thai"):
    voice_file = Path(f"Voices/Greetings/greeting_{language}.m4a")
    if not voice_file.exists():
        # Fallback to Thai
        voice_file = Path("Voices/Greetings/greeting_thai.m4a")
    # ...
```

---

## Quick Debug Checklist

If Follow Event not working:
1. ✅ Check Railway logs for "New follower!"
2. ✅ Check LINE webhook logs (manager.line.biz)
3. ✅ Verify FollowEvent import (line 30)
4. ✅ Verify handler registration (line 1245)
5. ✅ Check if voice file exists (Railway: `ls greeting_voice.m4a`)
6. ✅ Test voice endpoint: `https://your-app.railway.app/greeting-voice`

---

## Current Files

Voice files in project:
```
/Voices/Greetings/CN1.mp3 (278K)
/Voices/Greetings/CN2.mp3 (139K)
/Voices/Greetings/CN3.flac (692K)
/Voices/Greetings/CN4.m4a (178K) ← Using this one
/greeting_voice.m4a (copy of CN4.m4a)
```

Need to add:
```
/Voices/Greetings/greeting_thai.m4a
/Voices/Greetings/greeting_english.m4a
/Voices/Greetings/greeting_russian.m4a
/Voices/Greetings/greeting_japanese.m4a
/Voices/Greetings/greeting_korean.m4a
/Voices/Greetings/greeting_french.m4a
```

---

## Testing Plan (After Compact)

1. **Test Follow Event:**
   - Check Railway logs
   - Use second LINE account to add bot
   - Verify instant welcome received

2. **Fix Voice Language:**
   - Generate 6 more voice files (already have Chinese)
   - Update code to use dynamic voice URL
   - Deploy and test

3. **Verify Complete Flow:**
   - User adds bot → Voice in Thai + Welcome in Thai
   - User sends "EN" → Confirmation
   - Next follow → Voice in English + Welcome in English

---

## Environment Status

**Railway URL:** (need to check with `railway status`)
**LINE Bot ID:** @cannapeace
**Google Sheet ID:** 1Rz1DbllW-0ezJKM4Qsf58D8WAMPxuP5HOXzAbVgMQIY

**Latest Commits:**
- db3c9dc - Follow Event handler (just deployed)
- ff42de0 - Chinese voice greeting
- f7344c3 - Voice + text greeting system
- e4c3358 - Direct redirect attribution

---

## Priority After Compact

1. **URGENT:** Test if Follow Event works (check logs)
2. **HIGH:** Generate other 6 language voice files
3. **HIGH:** Fix voice to be language-dynamic
4. **MEDIUM:** Test complete flow end-to-end

---

## Questions to Answer

1. Is Follow Event actually triggering? (check logs)
2. Do we get "New follower!" in Railway logs when someone adds bot?
3. Is voice message sending? (check LINE)
4. Is welcome text sending? (check LINE)
5. Are we happy with Chinese voice quality for default?

---

Ready to resume after compact! 🚀
