# API Usage Optimization Analysis

**Date:** 2026-07-15
**Current Model:** Claude Sonnet 4 ($3/M input tokens, $15/M output tokens)

---

## 📊 CURRENT USAGE ANALYSIS

### Requests Currently Using Claude API:
1. ✅ **Menu requests** - "ดูเมนู", "menu", etc.
2. ✅ **Strain information** - "Tell me about Apple Banana"
3. ✅ **Recommendations** - "Recommend for sleep"
4. ✅ **General chat** - "How are you?", "Thanks!"
5. ✅ **Ordering** - "Order 3.5g Apple Banana"

### Requests Already Bypassing Claude (Optimized):
1. ✅ **About Us page** - Static content
2. ✅ **How to Order page** - Static content
3. ✅ **Contact page** - Static content
4. ✅ **Language selection** - Static Quick Reply
5. ✅ **Age gate** - Static compliance flow
6. ✅ **First message welcome** - Static greeting
7. ✅ **Underage blocking** - Static response

### Current Prompt Size Per Request:
```
Nancy persona prompt:     ~500 tokens
Product catalog:          ~200 tokens
Conversation history:     ~100-300 tokens (last 10 messages)
Instructions:             ~300 tokens
Customer message:         ~50-200 tokens
-------------------------------------------
TOTAL INPUT:              ~1,150-1,550 tokens per request
AVERAGE OUTPUT:           ~500-1,500 tokens
```

### Cost Per Request (Estimated):
- Input: 1,300 tokens avg × $3/M = $0.0039
- Output: 1,000 tokens avg × $15/M = $0.015
- **Total per request: ~$0.019 (2 cents)**

**If 100 customers, 10 messages each = 1,000 requests:**
- Daily cost: ~$19
- Monthly cost: ~$570

---

## 🎯 OPTIMIZATION OPPORTUNITIES

### HIGH IMPACT (Implement Immediately)

#### 1. **Menu Response Caching** 🔥
**Problem:** Menu is always the same, but goes to Claude every time
**Solution:** Detect menu keywords → Return cached menu directly
**Savings:** ~80 tokens input + ~500 tokens output = **$0.0075 saved per menu request**
**Impact:** If 30% of requests are menu → **$171/month savings**

**Implementation:**
```python
# Detect menu request BEFORE Claude
menu_keywords = ['menu', 'ดูเมนู', '菜单', 'меню', 'メニュー', '메뉴']
if any(k in message_lower for k in menu_keywords):
    # Return pre-formatted menu with strain Quick Reply buttons
    return cached_menu_response(language)
```

#### 2. **Strain Info Pre-Generation** 🔥
**Problem:** Strain descriptions are always the same, but generated fresh each time
**Solution:** Pre-generate all 7 strain descriptions × 7 languages = 49 cached responses
**Savings:** ~1,000 tokens input + ~800 tokens output = **$0.015 saved per strain request**
**Impact:** If 40% of requests are strain info → **$228/month savings**

**Implementation:**
```python
# Pre-generated strain responses in all languages
STRAIN_CACHE = {
    'thai': {
        'Apple Banana': "🌿 **Apple Banana** - Sativa 24% THC\n\n...",
        'Miracle Mints': "🌿 **Miracle Mints** - Hybrid 28% THC\n\n...",
        # ... all 7 strains
    },
    'english': { ... },
    # ... all 7 languages
}

# Detect strain request
if detected_strain:
    return STRAIN_CACHE[language][strain_name]
```

#### 3. **FAQ Auto-Responses** 🔥
**Problem:** Common questions answered repeatedly by Claude
**Solution:** Detect FAQ patterns → Return cached answers
**Savings:** ~1,200 tokens input + ~400 tokens output = **$0.0096 saved per FAQ**
**Impact:** If 15% of requests are FAQs → **$43/month savings**

**Common FAQs:**
- "Do you deliver?" / "ส่งได้ไหม"
- "How long is delivery?" / "ส่งนานแค่ไหน"
- "What's the minimum order?" / "สั่งขั้นต่ำเท่าไหร่"
- "Do you have CBD products?" / "มี CBD ไหม"
- "Are you open now?" / "เปิดไหม"
- "What payment methods?" / "จ่ายยังไง"

#### 4. **Simple Greeting Detection** 🔥
**Problem:** "hi", "hello", "thanks" don't need full Nancy AI
**Solution:** Pattern match simple greetings → Return friendly response
**Savings:** ~1,200 tokens input + ~200 tokens output = **$0.0066 saved**
**Impact:** If 10% of requests are greetings → **$20/month savings**

**Patterns:**
- Greetings: "hi", "hello", "สวัสดี", "你好", etc.
- Thanks: "thank you", "thanks", "ขอบคุณ", "谢谢", etc.
- Chitchat: "how are you", "สบายดีไหม", etc.

**Responses:**
```python
GREETINGS = {
    'thai': "สวัสดีค่ะ! 😊 มีอะไรให้ช่วยไหมคะวันนี้?",
    'english': "Hey! 😊 What can I help you with today?",
    # ...
}
```

---

### MEDIUM IMPACT (Consider Implementing)

#### 5. **Use Claude Haiku for Simple Questions**
**Cost Comparison:**
- Sonnet: $3 input / $15 output per M tokens
- Haiku: $0.25 input / $1.25 output per M tokens
- **12x cheaper!**

**When to use Haiku:**
- Simple menu requests
- Basic strain questions
- General chitchat
- Non-ordering conversations

**When to use Sonnet:**
- Order processing (needs accuracy)
- Complex recommendations
- Multi-turn conversations

**Implementation:**
```python
# Simple question detection
is_simple = (
    any(k in msg for k in menu_keywords) or
    len(message_text.split()) < 10 or
    no_order_intent_detected
)

model = "claude-haiku-3-5" if is_simple else "claude-sonnet-4-6"
```

#### 6. **Shorten Nancy Persona Prompt**
**Current:** ~500 tokens
**Optimized:** ~250 tokens

Remove verbose parts, keep essential personality:
```python
prompt = f"""You are Nancy from CannaPeace - 22yo Chula pharmacy grad specializing in cannabis.

Tone: Warm, friendly, knowledgeable. {lang_instruction}
Style: Conversational, not corporate. Use 😊🌿 sparingly.

Products:
{products_info}

History: {history_text}

Message: {message_text}

Respond naturally:"""
```

**Savings:** ~250 tokens × $3/M = **$0.00075 per request**
**Impact:** ~$22/month

#### 7. **Response Caching (5-Minute TTL)**
Cache identical questions for 5 minutes:
```python
response_cache = {}  # {(user_id, message_hash): (response, timestamp)}

cache_key = (user_id, hash(message_text.lower()))
if cache_key in response_cache:
    cached_response, timestamp = response_cache[cache_key]
    if time.time() - timestamp < 300:  # 5 minutes
        return cached_response
```

**Savings:** Avoids duplicate requests from same user
**Impact:** ~5-10% reduction

---

## 📈 PROJECTED SAVINGS SUMMARY

### After Implementing High-Impact Optimizations:

| Optimization | Current Cost | After Cost | Savings | % Reduction |
|--------------|-------------|-----------|---------|-------------|
| Menu caching | $171/mo | $0/mo | **$171/mo** | 100% |
| Strain info cache | $228/mo | $0/mo | **$228/mo** | 100% |
| FAQ responses | $43/mo | $0/mo | **$43/mo** | 100% |
| Simple greetings | $20/mo | $0/mo | **$20/mo** | 100% |
| **TOTAL** | **$570/mo** | **$108/mo** | **$462/mo** | **81%** |

### After Adding Medium-Impact Optimizations:

| Additional | Savings |
|------------|---------|
| Use Haiku for simple questions | **$30/mo** |
| Shorter prompts | **$22/mo** |
| Response caching | **$10/mo** |
| **TOTAL ADDITIONAL** | **$62/mo** |

### **GRAND TOTAL POTENTIAL SAVINGS:**
- **Before:** $570/month
- **After:** $46/month
- **Savings:** $524/month (92% reduction!)

---

## 🚀 IMPLEMENTATION PRIORITY

### Phase 1 (This Week) - High Impact:
1. ✅ Menu response caching
2. ✅ FAQ auto-responses
3. ✅ Simple greeting detection
4. ⚠️ Strain info pre-generation (49 responses to create)

### Phase 2 (Next Week) - Medium Impact:
1. Use Haiku for simple questions
2. Shorten Nancy persona prompt
3. Implement response caching

### Phase 3 (Optional) - Advanced:
1. Analytics dashboard for API usage
2. A/B testing Haiku vs Sonnet quality
3. Dynamic model selection based on complexity

---

## 💡 ADDITIONAL BENEFITS

Beyond cost savings:

1. **Faster responses** - Cached responses return instantly (no API call)
2. **Better UX** - No waiting for AI to "think" on simple questions
3. **Reliability** - Cached responses work even if Claude API is down
4. **Consistency** - Menu always formatted perfectly
5. **Scalability** - Can handle 10x traffic without 10x cost

---

## 📊 MONITORING RECOMMENDATIONS

Track these metrics:

1. **API calls per day** (before/after)
2. **Cache hit rate** (% of requests served from cache)
3. **Average tokens per request** (should decrease)
4. **Total monthly cost** (should drop 80-90%)
5. **Response time** (should improve)
6. **Customer satisfaction** (should stay same or improve)

---

## ⚠️ IMPORTANT NOTES

**Don't optimize prematurely:**
- Keep Claude for order processing (accuracy critical!)
- Keep Claude for complex recommendations
- Keep Nancy's personality intact

**Quality checks:**
- Test cached responses in all 7 languages
- Ensure FAQ answers are accurate
- Update cache when products change

**Maintenance:**
- Update strain cache when menu changes
- Update FAQ cache when policies change
- Review cache hit rates monthly

---

**Recommended Action:** Implement Phase 1 immediately (2-3 hours of work, $462/month savings!)
