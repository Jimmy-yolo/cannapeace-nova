# Greeting System - Voice + Text

## Overview
CannaPeace bot sends **voice message + text message** on first customer contact.

---

## First Message (New Customer)

**What happens:**
1. Customer sends first message (e.g., "hi", "hello", "สวัสดี")
2. Bot sends **2 messages**:
   - ✅ **Voice message** (10 seconds): "สวัสดีค่ะ! ยินดีต้อนรับสู่แคนนาพีซ"
   - ✅ **Text message**: Greeting + language options

**Text greeting format:**
```
สวัสดีค่ะ! ยินดีต้อนรับสู่ CannaPeace 🌿

🌐 **เปลี่ยนภาษา / Switch Language:**
พิมพ์รหัสภาษาเพื่อเปลี่ยน:
TH | EN | 中文 | RU | 日本語 | 한국어 | FR
```

---

## Regular Messages (Existing Customer)

**When customer says "Hi" or "Hello":**
- Claude AI responds with warm greeting in customer's language
- Examples:
  - Thai: "สวัสดีค่ะ! มีอะไรให้ช่วยไหมคะวันนี้?"
  - English: "Hello! How can I help you today?"
  - Chinese: "你好！今天有什么可以帮您的？"

No voice message sent (only on very first contact).

---

## Voice Message Setup

### Current Status
Voice greeting endpoint is ready at `/greeting-voice`

### To Add Voice Greeting

**Option 1: Upload Audio File**
1. Record voice message saying: "สวัสดีค่ะ! ยินดีต้อนรับสู่แคนนาพีซ"
2. Save as `greeting_voice.m4a` (M4A format, ~10 seconds)
3. Upload to Railway project root
4. Bot will automatically send it on first messages

**Option 2: Use Text-to-Speech**
1. Use online TTS service (e.g., Google Cloud TTS, ElevenLabs)
2. Generate Thai voice: "สวัสดีค่ะ! ยินดีต้อนรับสู่แคนนาพีซ"
3. Download as M4A
4. Upload to Railway as `greeting_voice.m4a`

**Option 3: Disable Voice (Text Only)**
If you don't want voice greeting, the code will handle it gracefully:
- If `greeting_voice.m4a` doesn't exist, bot sends text only
- No errors, just skips voice message

---

## Code Location

**Greeting logic:** `app.py` lines 867-890
```python
if is_first_message:
    greeting = get_greeting_message(current_language)
    if line_bot_api:
        messages = []

        # Voice message
        messages.append(AudioSendMessage(...))

        # Text message
        messages.append(TextSendMessage(text=greeting))

        line_bot_api.reply_message(event.reply_token, messages)
```

**Voice endpoint:** `app.py` lines 1765-1781
```python
@app.get("/greeting-voice")
async def serve_greeting_voice():
    voice_file = Path("greeting_voice.m4a")
    if voice_file.exists():
        return FileResponse(voice_file, media_type="audio/m4a")
    else:
        raise HTTPException(status_code=404)
```

---

## Environment Variables

Add to Railway:
```
LINE_BOT_ID=@cannapeace
```

This is used for:
- Attribution link redirects
- Greeting system
- All LINE bot references

---

## Testing

**Test First Message:**
1. Delete your user from Customers sheet
2. Send "hi" to bot
3. Should receive:
   - Voice message (if greeting_voice.m4a exists)
   - Text with greeting + language options

**Test Regular Greeting:**
1. As existing customer, send "hi"
2. Should receive: Claude AI warm greeting (text only, no voice)

**Test Language Switch:**
1. Send "EN"
2. Should receive confirmation in English
3. Send "hi" again
4. Should receive greeting in English

---

## Audio File Requirements

**Format:** M4A (recommended) or MP3
**Duration:** ~10 seconds
**Content:** "สวัสดีค่ะ! ยินดีต้อนรับสู่แคนนาพีซ"
**File name:** `greeting_voice.m4a`
**Location:** Project root directory (same level as app.py)

LINE requires:
- HTTPS URL (Railway provides this automatically)
- Publicly accessible endpoint
- Valid audio format

---

## Summary

**First Contact:**
- Voice: "สวัสดีค่ะ! ยินดีต้อนรับสู่แคนนาพีซ" (10s)
- Text: Greeting + language options

**Regular Messages:**
- Text only: Claude AI warm greeting

**Voice File:**
- Optional: Upload `greeting_voice.m4a` to enable
- Works without it (text-only mode)
