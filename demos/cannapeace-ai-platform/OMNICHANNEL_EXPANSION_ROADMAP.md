# CannaPeace AI Platform - Omnichannel Expansion Roadmap

## 🎯 Vision: Complete Customer Engagement Ecosystem

**CannaPeace AI Platform** = One unified AI system powering customer engagement across ALL channels

### Current State (v1.0)
✅ LINE Official Account
- AI customer service (Claude)
- Strain recommendations with images
- Order processing
- Conversation memory
- Performance monitoring

### Future State (v3.0)
🚀 **Omnichannel Customer Engagement Platform**
- LINE, Facebook Messenger, Instagram DM, TikTok Chat
- Social media auto-reply (comments on posts)
- Unified customer profiles across all channels
- Cross-channel attribution
- Centralized analytics dashboard

---

## 📱 Multi-Channel Expansion Plan

### Phase 1: LINE (COMPLETE ✅)
**Status:** v1.0 production-ready
**Features:**
- ✅ AI-powered conversations (Thai/English)
- ✅ Product recommendations
- ✅ Order placement & Google Sheets tracking
- ✅ Typing indicators
- ✅ Performance monitoring
- ✅ Strain image auto-reply

**Metrics:**
- Response time: 2-4 seconds
- Cost per conversation: ~฿0.02
- Uptime: 99.9%

---

### Phase 2: Facebook Messenger Integration
**Timeline:** Week 1-3 after v2.0 CRM
**Effort:** 2-3 weeks
**Status:** Planned

#### Why Facebook Messenger?
- ✅ 2nd most popular messaging app in Thailand (after LINE)
- ✅ Older demographic (35-55 years old)
- ✅ Facebook Shop integration potential
- ✅ Wider reach internationally

#### Technical Implementation

**1. Facebook App Setup**
```
1. Create Facebook App (Meta for Developers)
2. Add Messenger product
3. Generate Page Access Token
4. Subscribe to webhook events
5. Set webhook URL: https://your-domain.com/webhook/messenger
```

**2. Code Changes**
```python
# Add to app.py
from fbmessenger import BaseMessenger
from fbmessenger import templates, elements, quick_replies

class MessengerHandler:
    def __init__(self, page_access_token):
        self.messenger = BaseMessenger(page_access_token)

    async def handle_message(self, sender_id, message_text):
        # Use same Claude AI logic as LINE
        response = await process_with_claude(message_text)

        # Send via Messenger API
        self.messenger.send(recipient_id=sender_id, message=response)

@app.post("/webhook/messenger")
async def messenger_webhook(request: Request):
    data = await request.json()

    if data.get("object") == "page":
        for entry in data["entry"]:
            for event in entry["messaging"]:
                if "message" in event:
                    sender_id = event["sender"]["id"]
                    message_text = event["message"]["text"]

                    await messenger_handler.handle_message(sender_id, message_text)

    return {"status": "ok"}
```

**3. Unified Message Processing**
```python
# Create unified handler that works for all platforms
class UnifiedMessageHandler:
    async def process_message(self, platform, user_id, message_text):
        # Same Claude AI logic for all platforms
        response = await claude_ai.generate_response(
            message=message_text,
            conversation_history=get_history(platform, user_id),
            user_profile=get_customer_profile(user_id)
        )

        # Platform-specific sending
        if platform == "line":
            await line_bot.send(user_id, response)
        elif platform == "messenger":
            await messenger_bot.send(user_id, response)

        # Log to unified database
        await log_message(platform, user_id, message_text, response)
```

**4. Customer Profile Linking**
```python
# Link Messenger ID to customer profile
def link_messenger_user(messenger_id, phone_number):
    customer = get_customer_by_phone(phone_number)
    if customer:
        customer.messenger_id = messenger_id
        customer.save()
    else:
        create_customer(messenger_id=messenger_id, acquisition_source="messenger")
```

**Features:**
- ✅ Same Claude AI conversational engine
- ✅ Strain recommendations with images
- ✅ Order processing
- ✅ Messenger-specific features: Quick Replies, Buttons, Carousels
- ✅ Attribution tracking (know which FB post brought them)

**Cost:** $0 (Messenger API is free)

---

### Phase 3: Instagram DM Integration
**Timeline:** Week 4-6
**Effort:** 2 weeks
**Status:** Planned

#### Why Instagram DM?
- ✅ Younger demographic (18-35 years old)
- ✅ Visual platform (perfect for product images)
- ✅ Instagram Shopping integration
- ✅ Strong engagement rates
- ✅ Influencer marketing channel

#### Technical Implementation

**1. Instagram Business Account Setup**
```
1. Convert to Instagram Business Account
2. Connect to Facebook Page
3. Use same Facebook App as Messenger
4. Subscribe to Instagram webhook events
5. Webhook URL: https://your-domain.com/webhook/instagram
```

**2. Code Changes**
```python
# Similar to Messenger, using Instagram Graph API
class InstagramDMHandler:
    async def handle_dm(self, sender_id, message_text):
        # Same unified handler
        await unified_handler.process_message(
            platform="instagram",
            user_id=sender_id,
            message_text=message_text
        )

@app.post("/webhook/instagram")
async def instagram_webhook(request: Request):
    data = await request.json()
    # Handle Instagram DM events
    # Similar structure to Messenger webhook
```

**Instagram-Specific Features:**
- ✅ Send product images directly in DM
- ✅ Story mention replies
- ✅ Comment to DM (public comment → auto-DM)
- ✅ Instagram Shop product links

**Cost:** $0 (Instagram API is free)

---

### Phase 4: TikTok Chat Integration
**Timeline:** Week 7-9
**Effort:** 2-3 weeks
**Status:** Planned

#### Why TikTok?
- ✅ Fastest growing platform in Thailand
- ✅ Young demographic (16-30 years old)
- ✅ Viral content potential
- ✅ TikTok Shop integration
- ✅ High engagement rates

#### Technical Implementation

**1. TikTok for Business Setup**
```
1. Apply for TikTok for Business API access
2. Create TikTok app
3. Enable Messaging API
4. Set webhook URL
```

**2. Code Changes**
```python
class TikTokChatHandler:
    async def handle_chat(self, user_id, message_text):
        await unified_handler.process_message(
            platform="tiktok",
            user_id=user_id,
            message_text=message_text
        )

@app.post("/webhook/tiktok")
async def tiktok_webhook(request: Request):
    # Handle TikTok chat events
    pass
```

**TikTok-Specific Features:**
- ✅ Video responses (send strain overview videos)
- ✅ TikTok Shop product links
- ✅ Live stream chat integration
- ✅ Comment to chat (video comment → auto-chat)

**Cost:** $0 (TikTok API is free)

**Note:** TikTok API access requires approval - apply 2-3 weeks in advance

---

## 💬 Social Media Auto-Reply System

### Phase 5: Intelligent Comment Management
**Timeline:** Week 10-14
**Effort:** 4 weeks
**Status:** Planned

This is a **game-changer** - automatically respond to comments on your social media posts!

### How It Works

```
Customer comments on your TikTok video →
AI analyzes comment →
Classifies intent →
Takes appropriate action
```

### Comment Classification & Actions

#### Type 1: Questions ❓
**Examples:**
- "What's the THC %?"
- "Do you deliver to Chiang Mai?"
- "Is this indica or sativa?"

**Action:** Auto-reply with answer
```
AI Response: "Hi! This is Miracle Mints, a hybrid with 28% THC.
We deliver nationwide! DM us to order 🌿"
```

#### Type 2: Positive Comments ✅
**Examples:**
- "Looks amazing!"
- "I want to try this"
- "Beautiful buds"

**Action:** Like + emoji reaction
```
Action: ❤️ Like the comment
Optional: Add fire emoji 🔥 or leaf emoji 🌿
```

#### Type 3: Issues/Complaints ⚠️
**Examples:**
- "My order never arrived"
- "This wasn't what I expected"
- "Price is too high"

**Action:** Alert operator + template response
```
Action:
1. Notify operator via LINE/email
2. Post template: "We're sorry to hear that! Please DM us so we can help 🙏"
3. Flag for human follow-up
```

#### Type 4: Spam/Inappropriate 🚫
**Examples:**
- Competitor links
- Unrelated content
- Offensive language

**Action:** Hide/delete (or alert for review)
```
Action: Hide comment (Facebook/Instagram)
       OR flag for manual review
```

### Technical Implementation

#### Architecture
```
Social Platform → Webhook → AI Classifier → Action Handler → Response
```

#### 1. Webhook Setup (Per Platform)

**Facebook/Instagram:**
```python
@app.post("/webhook/facebook-comments")
async def facebook_comment_webhook(request: Request):
    data = await request.json()

    for entry in data["entry"]:
        if "changes" in entry:
            for change in entry["changes"]:
                if change["field"] == "feed":
                    comment_id = change["value"]["comment_id"]
                    comment_text = change["value"]["message"]
                    post_id = change["value"]["post_id"]

                    await process_comment(
                        platform="facebook",
                        comment_id=comment_id,
                        text=comment_text,
                        post_id=post_id
                    )
```

**TikTok:**
```python
@app.post("/webhook/tiktok-comments")
async def tiktok_comment_webhook(request: Request):
    # Similar structure for TikTok video comments
    pass
```

#### 2. AI Comment Classifier
```python
async def classify_comment(comment_text):
    prompt = f"""Classify this social media comment about cannabis products:

Comment: "{comment_text}"

Classify as one of:
1. QUESTION - asking about product, delivery, price, etc.
2. POSITIVE - expressing interest or praise
3. ISSUE - complaint, problem, negative feedback
4. SPAM - unrelated, promotional, offensive

Also extract:
- Intent details (what they're asking/saying)
- Sentiment (positive/neutral/negative)
- Urgency (low/medium/high)

Return JSON:
{{
  "category": "QUESTION|POSITIVE|ISSUE|SPAM",
  "intent": "brief description",
  "sentiment": "positive|neutral|negative",
  "urgency": "low|medium|high",
  "suggested_response": "auto-reply text or null"
}}
"""

    response = await claude_ai.classify(prompt)
    return response
```

#### 3. Action Handler
```python
async def handle_comment(classification, comment_id, platform):
    if classification["category"] == "QUESTION":
        # Auto-reply with answer
        reply_text = classification["suggested_response"]
        await post_comment_reply(platform, comment_id, reply_text)

        # Log for analytics
        log_comment_interaction("question_answered", platform, comment_id)

    elif classification["category"] == "POSITIVE":
        # Like the comment
        await like_comment(platform, comment_id)

        # Optional: Add reaction emoji
        if random.random() < 0.3:  # 30% of the time
            await add_reaction(platform, comment_id, emoji="❤️")

    elif classification["category"] == "ISSUE":
        # Alert operator
        await notify_operator(
            channel="line",  # Send LINE message to owner
            message=f"⚠️ Issue on {platform}:\n\n{comment_text}\n\nLink: {comment_url}"
        )

        # Post empathetic template response
        template = "We're sorry to hear that! Please DM us so we can make this right 🙏"
        await post_comment_reply(platform, comment_id, template)

        # Flag for human follow-up
        flag_for_review(comment_id, priority="high")

    elif classification["category"] == "SPAM":
        # Hide or flag for review (don't auto-delete)
        await hide_comment(platform, comment_id)
        log_spam(platform, comment_id)
```

#### 4. Platform-Specific APIs

**Facebook/Instagram (Graph API):**
```python
import requests

async def post_comment_reply(platform, comment_id, text):
    url = f"https://graph.facebook.com/v18.0/{comment_id}/replies"
    params = {
        "message": text,
        "access_token": FB_PAGE_ACCESS_TOKEN
    }
    response = requests.post(url, json=params)
    return response.json()

async def like_comment(platform, comment_id):
    url = f"https://graph.facebook.com/v18.0/{comment_id}/likes"
    params = {"access_token": FB_PAGE_ACCESS_TOKEN}
    response = requests.post(url, json=params)
```

**TikTok:**
```python
async def reply_to_tiktok_comment(video_id, comment_id, text):
    # TikTok API (when available)
    # Currently limited - may need manual review workflow
    pass
```

### Features & Capabilities

#### Auto-Reply Intelligence
- ✅ Understands Thai and English
- ✅ Context-aware (knows which product post)
- ✅ Personalized responses
- ✅ Maintains brand voice
- ✅ Includes call-to-action (DM us, check bio, etc.)

#### Operator Dashboard
```
Real-time comment feed:
┌─────────────────────────────────────┐
│ 🟢 Question - Auto-replied          │
│ TikTok: "What's the price?"         │
│ Replied: "450฿ per 10g! DM to order"│
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ ⚠️ Issue - NEEDS ATTENTION          │
│ Facebook: "Order never came"        │
│ Notified: Owner via LINE            │
│ [View] [Reply] [Resolve]            │
└─────────────────────────────────────┘
```

#### Analytics
- Comment volume by platform
- Response rate & time
- Sentiment analysis (% positive/negative)
- Top questions (FAQ insights)
- Engagement rate (likes/replies on auto-responses)

### Safety & Controls

#### Manual Review Queue
- All "ISSUE" comments go to operator
- Optional: Review all auto-replies before posting
- Approve/edit/reject AI responses
- Blocklist certain keywords (auto-flag)

#### Rate Limiting
- Max 5 auto-replies per minute (avoid spam detection)
- Cooldown period between replies
- Don't reply to same user twice in 1 hour

#### Brand Safety
- Pre-approved response templates
- Keyword filtering (never mention illegal topics)
- Tone validation (always friendly, helpful)
- Compliance checks (age verification reminders)

---

## 🏗️ Unified Architecture

### Current (v1.0) - Single Channel
```
LINE Customer → LINE Bot → Claude AI → Google Sheets
```

### Future (v3.0) - Omnichannel
```
LINE Customer      ─┐
Messenger Customer ─┤
Instagram Customer ─┼→ Unified Handler → Claude AI ─┐
TikTok Customer    ─┤                                 │
Social Comment     ─┘                                 │
                                                      ↓
                                            ┌─────────────────┐
                                            │ Customer Profile│
                                            │ (unified across │
                                            │  all channels)  │
                                            └─────────────────┘
                                                      ↓
                                            ┌─────────────────┐
                                            │ PostgreSQL DB   │
                                            │ + Google Sheets │
                                            └─────────────────┘
```

### Unified Customer Profile
```python
class Customer:
    # Identifiers across platforms
    line_id: str = None
    messenger_id: str = None
    instagram_id: str = None
    tiktok_id: str = None

    # Unified data
    phone: str
    name: str
    acquisition_source: str  # "line", "messenger", "instagram", "tiktok", "facebook_comment"
    lifetime_value: float
    total_orders: int
    favorite_strains: List[str]

    # Channel preferences
    preferred_channel: str  # Which platform they use most
    last_contact_channel: str
    active_channels: List[str]  # ["line", "instagram"]
```

---

## 📊 Multi-Channel Attribution

### Tracking Customer Source

**Scenario:** Customer sees TikTok video → Comments → Clicks bio link → Chats on LINE → Orders

**Tracking:**
```python
# Attribution chain
customer.acquisition_source = "tiktok"
customer.utm_campaign = "tiktok-food-account"
customer.utm_medium = "video-comment"
customer.first_touchpoint = "tiktok_comment"
customer.conversion_channel = "line"

# Journey
1. TikTok comment (2024-07-14 10:00)
2. Clicked bio link (2024-07-14 10:05)
3. LINE chat started (2024-07-14 10:10)
4. Order placed (2024-07-14 10:45)
```

**Analytics:**
```
TikTok Food Account Performance:
- Total views: 50,000
- Comments: 500
- Comment-to-order rate: 2% (10 orders)
- Revenue: ฿4,500
- ROI: Infinite (organic content)
```

---

## 💰 Cost Analysis (Multi-Channel)

### Platform API Costs

| Platform | API Cost | Notes |
|----------|----------|-------|
| LINE | Free | Messaging API included |
| Facebook Messenger | Free | Graph API free tier |
| Instagram DM | Free | Same as Messenger |
| TikTok Chat | Free | Once approved |
| **Total Platform Costs** | **฿0/month** | All free! |

### Only Cost: Claude AI
- Same cost per conversation (~฿0.02) regardless of platform
- 1000 conversations/month across all channels: ฿20
- 10,000 conversations/month: ฿200

### Total Monthly Costs (v3.0)

| Component | Cost |
|-----------|------|
| Railway hosting | ฿360 |
| Claude AI (1000 conv) | ฿20-50 |
| Google Sheets | Free |
| LINE, Messenger, Instagram, TikTok APIs | Free |
| **Total** | **฿380-410/month** |

**Even with 5 platforms, cost stays under ฿500/month!**

---

## 📈 Expected Impact

### Reach Expansion
- **LINE:** 40M users in Thailand
- **+ Facebook Messenger:** +30M users
- **+ Instagram:** +15M users
- **+ TikTok:** +25M users
- **Total potential:** 110M touchpoints

### Customer Acquisition
- **Current (LINE only):** 10-20 customers/month
- **With all channels:** 50-100 customers/month (5x increase)

### Engagement
- **Social auto-reply:** 10-30 comments/day
- **Question answered instantly:** 95% response rate
- **Operator time saved:** 2-3 hours/day

---

## 🚀 Implementation Timeline

### Month 1: CRM Foundation (Current)
- ✅ LINE bot v1.0
- 🔄 Add customer profiles
- 🔄 Add journey tracking
- 🔄 Add attribution

### Month 2: Messenger + Instagram
- Week 1-2: Messenger integration
- Week 3-4: Instagram DM integration
- Test with small customer base

### Month 3: TikTok + Social Auto-Reply
- Week 1-2: TikTok Chat integration
- Week 3-4: Social comment auto-reply
- Deploy to production

### Month 4: Optimization
- Analytics dashboards
- A/B test response templates
- Refine AI prompts
- Scale to high volume

---

## 🎯 Success Metrics

### Platform KPIs
- Messages per platform per day
- Response time by platform
- Conversion rate by platform
- Customer acquisition cost by platform

### Engagement KPIs
- Comment response rate
- Positive sentiment %
- Questions answered automatically
- Operator alerts (issues flagged)

### Business KPIs
- Total customers across all channels
- Revenue by acquisition channel
- Customer lifetime value by channel
- Repeat purchase rate

---

## 🔮 Future Possibilities (v4.0+)

### WhatsApp Business
- Popular internationally
- WhatsApp Business API

### Twitter/X DM
- Niche but engaged audience
- Developer API available

### Email Integration
- Newsletter responses
- Order confirmation replies

### Voice/Phone
- AI voice assistant for phone orders
- Twilio integration

### Web Chat Widget
- Embed on website
- Same AI, different interface

---

## Summary

**CannaPeace AI Platform = One brain, many mouths**

✅ Same Claude AI intelligence
✅ Same strain recommendations
✅ Same order processing
✅ Unified customer profiles
✅ Cross-channel attribution
✅ Social auto-reply

**One codebase, 5+ platforms, unlimited growth potential!**

**Next steps:** Complete v2.0 CRM, then add Messenger (Month 2)
