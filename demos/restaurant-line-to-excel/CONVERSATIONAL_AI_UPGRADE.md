# Conversational AI Upgrade Guide

## Overview
Upgrade your LINE bot from a simple order parser to a full conversational AI customer service agent.

## Key Features of Conversational AI

### 1. Handles Greetings
**Before:**
- User: "Hi" → Bot: (tries to parse as order, fails)

**After:**
- User: "Hi" → Bot: "สวัสดีค่ะ! ยินดีต้อนรับสู่ CannaPeace 🌿 ต้องการสั่งสายพันธุ์ไหนดีคะ?"
- User: "Hello" → Bot: "Hello! Welcome to CannaPeace! How can I help you today?"

### 2. Asks for Missing Information
**Before:**
- User: "3g Thai Stick" → Bot: Confirms order without phone

**After:**
- User: "3g Thai Stick" → Bot: "ขอเบอร์โทรสำหรับจัดส่งหน่อยค่ะ"
- User: "081-234-5678" → Bot: "ขอที่อยู่จัดส่งด้วยค่ะ"
- User: "123 Sukhumvit" → Bot: "✅ ขอบคุณค่ะ! รับออเดอร์แล้ว..."

### 3. Answers Questions
- User: "What strains do you have?" → Bot: Lists all products with prices
- User: "What's the difference between Sativa and Indica?" → Bot: Explains
- User: "How much is Thai Stick?" → Bot: "Thai Stick is 400 baht per gram"

### 4. Remembers Conversation Context
- Tracks what user said before
- Continues conversations naturally
- Knows if order is incomplete

## Implementation Approach

### Option 1: Simple (Recommended for Start)
Add basic conversational prompt to existing code:

```python
# In handle_message function, change prompt to:
prompt = f\"\"\"You are a friendly customer service agent for CannaPeace cannabis shop.

Previous conversation:
{conversation_history}

Customer's new message: {message_text}

Your task:
1. If it's a greeting → Respond warmly in Thai/English
2. If it's a question → Answer helpfully
3. If it's an order:
   - Extract items, quantities
   - Ask for phone if missing
   - Ask for address if missing
   - Confirm when complete

Available products:
- Thai Stick (400฿/g) - Sativa 22% THC
- Mango Kush (350฿/g) - Hybrid 18% THC
- Northern Lights (450฿/g) - Indica 20% THC

Respond naturally. If order is complete, output JSON at the end:
ORDER_COMPLETE: {{json}}
\"\"\"
```

### Option 2: Advanced (Full Conversational Agent)
- Add conversation memory database
- Multi-turn state tracking
- Complex order validation
- Product recommendations

## Quick Implementation Steps

1. **Add conversation memory** (after line 77):
```python
# Conversation memory (user_id -> messages)
conversation_memory = {}
```

2. **Update handle_message** function (around line 328):
   - Get user ID: `user_id = event.source.user_id`
   - Load conversation history from memory
   - Use conversational prompt (see above)
   - Save conversation back to memory
   - Only save to sheet if "ORDER_COMPLETE" in response

3. **Parse bot response**:
   - If contains "ORDER_COMPLETE:" → Extract JSON, save to sheet
   - Otherwise → Just send reply, continue conversation

## Testing Examples

```
User: Hi
Bot: สวัสดีค่ะ! ยินดีต้อนรับสู่ CannaPeace 🌿

User: What do you have?
Bot: เรามีสายพันธุ์ดีๆ หลายแบบค่ะ:
     - Thai Stick 400฿/g (Sativa)
     - Mango Kush 350฿/g (Hybrid)
     ...

User: I want 3g Thai Stick
Bot: ขอเบอร์โทรสำหรับจัดส่งหน่อยค่ะ

User: 081-234-5678
Bot: ขอบคุณค่ะ! ขอที่อยู่จัดส่งด้วยนะคะ

User: 123 Sukhumvit Rd
Bot: ✅ รับออเดอร์แล้วค่ะ!
     🌿 รายการ: Thai Stick x3g
     💰 รวม: 1,200 บาท
     📍 จัดส่งไปที่: 123 Sukhumvit Rd
     ✨ ขอบคุณค่ะ - CannaPeace
```

## Benefits

1. **Better UX** - Customers can chat naturally
2. **Higher conversion** - Guides customers through ordering
3. **Fewer errors** - Validates all info before confirming
4. **More professional** - Feels like real customer service
5. **Scalable** - Easy to add new features (payment, tracking, etc.)

## Next Steps

Would you like me to:
1. **Quick Demo** - Create a test script to show how it works locally?
2. **Full Implementation** - Completely rewrite app.py with conversational AI?
3. **Gradual Upgrade** - Start with basic conversational prompts, add features later?

Let me know which approach you prefer!
