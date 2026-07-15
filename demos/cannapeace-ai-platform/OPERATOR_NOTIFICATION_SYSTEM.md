# Operator Notification System - Design Document

**Date:** 2026-07-15
**Purpose:** Enable human operators to intervene when customers need help or bot encounters issues

---

## OVERVIEW

When customers face difficulties or the bot can't handle a request, the system should:
1. **Detect** the issue automatically
2. **Notify** operators immediately
3. **Enable** seamless handoff to human chat

---

## 1. DETECTION TRIGGERS

### Automatic Detection Scenarios:

#### A) Customer Explicitly Requests Human
**Triggers:**
- "talk to human", "speak to operator", "customer service"
- "ต้องการพูดคุยกับคน", "ต้องการเจ้าหน้าที่"
- "人工服务", "转人工"

**Action:** Immediate operator notification

#### B) Bot Fails to Understand (3+ times)
**Triggers:**
- Customer sends same question 3 times
- Claude responds with "I don't understand" repeatedly
- Customer frustration detected ("this doesn't work", "not helpful")

**Action:** Suggest human operator

#### C) Complex Medical/Legal Questions
**Triggers:**
- Keywords: "medical", "prescription", "doctor", "legal", "law"
- Health-related questions bot shouldn't answer
- Regulatory compliance issues

**Action:** Auto-handoff to operator

#### D) Order Issues
**Triggers:**
- "cancel order", "wrong order", "didn't receive"
- "refund", "complaint", "problem with delivery"

**Action:** Flag for operator review

#### E) Technical Errors
**Triggers:**
- Python exceptions in bot code
- Claude API errors (rate limits, timeouts)
- Database connection failures

**Action:** Alert operator + send fallback message to customer

---

## 2. NOTIFICATION METHODS

### Option A: LINE Notify (EASIEST - RECOMMENDED)
**What:** Official LINE notification service
**Setup:** 10 minutes
**Cost:** FREE

**How it works:**
1. Create LINE Notify channel
2. Get notification token
3. Send POST request when trigger occurs
4. Operators get instant LINE notification

**Pros:**
- ✅ FREE
- ✅ Operators already use LINE
- ✅ Instant notifications
- ✅ Easy to set up
- ✅ No additional apps needed

**Cons:**
- ❌ One-way only (notify, but operator must go to LINE Official Account Manager to respond)

**Setup Steps:**
```python
# 1. Get LINE Notify token from https://notify-bot.line.me/
LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")

# 2. Send notification
def notify_operator(user_id, issue_type, message):
    headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
    data = {
        "message": f"\n🚨 Customer Needs Help!\n\nUser: {user_id}\nIssue: {issue_type}\nMessage: {message}\n\n👉 Open LINE Official Account Manager to respond"
    }
    requests.post("https://notify-api.line.me/api/notify", headers=headers, data=data)
```

---

### Option B: LINE Official Account Chat Mode
**What:** Switch from Bot mode to Chat mode
**Setup:** Configure in LINE Official Account Manager
**Cost:** FREE

**How it works:**
1. Bot detects issue
2. Bot sends message: "I'm connecting you to our team..."
3. Operator gets notification in LINE Official Account app
4. Operator chats directly with customer
5. When done, switch back to Bot mode

**Pros:**
- ✅ FREE
- ✅ Direct chat with customer
- ✅ Operator sees full chat history
- ✅ Built-in to LINE Official Account

**Cons:**
- ❌ Requires manual mode switching (or Messaging API automation)
- ❌ Operator must monitor LINE Official Account Manager

**Setup:**
Use LINE Messaging API's [Module Mode](https://developers.line.biz/en/docs/messaging-api/switching-to-chat-mode/):
```python
# Send notification to operators that customer needs help
# Operator manually takes over in LINE Official Account Manager
# Or use LINE Official Account API to programmatically switch modes
```

---

### Option C: Email Notifications
**What:** Email operators when issues occur
**Setup:** 15 minutes
**Cost:** FREE (using SendGrid/AWS SES free tier)

**How it works:**
1. Bot detects trigger
2. Sends email to operators@cannapeace.com
3. Email contains user ID, issue type, chat history
4. Operator logs into LINE Official Account Manager to respond

**Pros:**
- ✅ Works even if operators not on LINE
- ✅ Email record for auditing
- ✅ Can include full chat transcript

**Cons:**
- ❌ Not instant (email delays)
- ❌ Operator must still go to LINE to respond
- ❌ Requires email service setup

---

### Option D: Push Notifications (Mobile App)
**What:** Custom mobile app for operators
**Setup:** Months of development
**Cost:** $$$

**Skip this.** Not worth it for CannaPeace's scale.

---

## 3. RECOMMENDED IMPLEMENTATION

### **Phase 1: LINE Notify (Week 1)**
**Goal:** Instant operator notifications

```python
# Add to app.py

LINE_NOTIFY_TOKEN = os.getenv("LINE_NOTIFY_TOKEN")
OPERATOR_LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"

def detect_customer_issue(user_id, message_text, conversation_history):
    """Detect if customer needs human operator"""

    # Check for explicit operator request
    operator_keywords = [
        'talk to human', 'speak to operator', 'customer service', 'real person',
        'ต้องการพูดคุยกับคน', 'ต้องการเจ้าหน้าที่', 'คุยกับคน',
        '人工服务', '转人工', 'operator', 'помощь оператора'
    ]

    if any(keyword in message_text.lower() for keyword in operator_keywords):
        return "EXPLICIT_REQUEST"

    # Check for repeated questions (frustration)
    if len(conversation_history) >= 6:
        recent_user_messages = [msg['content'] for msg in conversation_history[-6:] if msg['role'] == 'user']
        if len(set(recent_user_messages)) <= 2:  # Same question repeated
            return "REPEATED_QUESTION"

    # Check for medical/legal questions
    sensitive_keywords = ['medical', 'prescription', 'doctor', 'health', 'legal', 'law', 'lawyer']
    if any(keyword in message_text.lower() for keyword in sensitive_keywords):
        return "SENSITIVE_TOPIC"

    # Check for order issues
    order_keywords = ['cancel', 'wrong order', 'didn\'t receive', 'refund', 'complaint', 'problem']
    if any(keyword in message_text.lower() for keyword in order_keywords):
        return "ORDER_ISSUE"

    return None

def notify_operator(user_id, issue_type, message, conversation_history=None):
    """Send LINE Notify to operators"""
    try:
        # Get customer info
        profile = get_customer_profile(user_id)
        customer_name = profile.get('name', 'Unknown') if profile else 'Unknown'
        phone = profile.get('phone', 'Not provided') if profile else 'Not provided'

        # Format chat history
        chat_summary = ""
        if conversation_history and len(conversation_history) > 0:
            chat_summary = "\n\n📜 Recent Chat:\n"
            for msg in conversation_history[-4:]:  # Last 4 messages
                role = "Customer" if msg['role'] == 'user' else "Bot"
                chat_summary += f"{role}: {msg['content'][:100]}...\n"

        # Send notification
        notification_text = f"""
🚨 Customer Needs Help!

👤 Customer: {customer_name}
📱 Phone: {phone}
🆔 LINE ID: {user_id}

⚠️ Issue Type: {issue_type}
💬 Last Message: {message}
{chat_summary}

👉 Open LINE Official Account Manager to respond:
https://manager.line.biz/
"""

        headers = {"Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"}
        data = {"message": notification_text}

        response = requests.post(OPERATOR_LINE_NOTIFY_URL, headers=headers, data=data)

        if response.status_code == 200:
            print(f"✅ Operator notified: {issue_type} for user {user_id}")
        else:
            print(f"❌ Failed to notify operator: {response.text}")

        return True

    except Exception as e:
        print(f"❌ Error notifying operator: {e}")
        return False

def send_handoff_message(user_id, event_reply_token, language='thai'):
    """Send message to customer that we're connecting them to operator"""

    handoff_messages = {
        'thai': "🙋‍♀️ กำลังเชื่อมต่อคุณกับทีมงานของเราค่ะ...\n\nเจ้าหน้าที่จะมาช่วยคุณในไม่ช้านะคะ 💬",
        'english': "🙋‍♀️ Connecting you to our team...\n\nAn operator will help you shortly! 💬",
        'chinese': "🙋‍♀️ 正在为您连接我们的团队...\n\n客服人员将很快为您服务！💬",
        'russian': "🙋‍♀️ Соединяем вас с нашей командой...\n\nОператор поможет вам в ближайшее время! 💬",
        'japanese': "🙋‍♀️ チームにお繋ぎしています...\n\nオペレーターがすぐに対応します！💬",
        'korean': "🙋‍♀️ 팀에 연결 중...\n\n상담원이 곧 도와드리겠습니다! 💬",
        'french': "🙋‍♀️ Connexion à notre équipe...\n\nUn opérateur vous aidera sous peu! 💬"
    }

    message = handoff_messages.get(language, handoff_messages['thai'])

    if line_bot_api:
        line_bot_api.reply_message(
            event_reply_token,
            TextSendMessage(text=message)
        )
```

### **Where to Add Detection:**

In `handle_message()` function, add after language detection:

```python
# Check if customer needs operator
issue_type = detect_customer_issue(user_id, message_text, conversation_history)

if issue_type:
    # Notify operators
    notify_operator(user_id, issue_type, message_text, conversation_history)

    # Tell customer we're connecting them
    send_handoff_message(user_id, event.reply_token, current_language)

    # Don't send Claude response, wait for operator
    return
```

---

### **Phase 2: Rich Menu with "Talk to Operator" Button (Week 2)**

Add permanent button in LINE chat for customers to request help:

```python
# Create Rich Menu (runs once via Messaging API)
rich_menu = {
    "size": {"width": 2500, "height": 843},
    "selected": True,
    "name": "Main Menu",
    "chatBarText": "Menu",
    "areas": [
        {
            "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},
            "action": {"type": "message", "text": "Menu"}
        },
        {
            "bounds": {"x": 833, "y": 0, "width": 834, "height": 843},
            "action": {"type": "message", "text": "Order"}
        },
        {
            "bounds": {"x": 1667, "y": 0, "width": 833, "height": 843},
            "action": {"type": "message", "text": "Talk to operator"}
        }
    ]
}
```

---

### **Phase 3: Error Monitoring (Week 3)**

Add try-catch around critical functions:

```python
# In handle_message()
try:
    # ... Claude API call ...
    response = anthropic_client.messages.create(...)

except anthropic.APIError as e:
    # API error - notify operator
    notify_operator(
        user_id,
        "BOT_ERROR",
        f"Claude API Error: {str(e)}",
        conversation_history
    )

    # Tell customer
    error_message = "I'm having trouble right now. Our team has been notified and will help you soon!"
    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=error_message))
    return

except Exception as e:
    # Unexpected error
    notify_operator(
        user_id,
        "SYSTEM_ERROR",
        f"Unexpected error: {str(e)}",
        conversation_history
    )
    # Send fallback message...
```

---

## 4. OPERATOR WORKFLOW

### When Notification Received:

1. **Operator gets LINE Notify**
   - "🚨 Customer Needs Help!"
   - Shows customer name, phone, issue type, chat history

2. **Operator opens LINE Official Account Manager**
   - https://manager.line.biz/
   - Finds customer in chat list
   - Sees full conversation history

3. **Operator responds directly**
   - Types message in LINE Official Account Manager
   - Customer receives message instantly
   - Continues conversation until resolved

4. **Operator marks resolved**
   - Bot resumes automatic responses
   - Or: keep manual mode for VIP customers

---

## 5. SETUP CHECKLIST

### Week 1: LINE Notify
- [ ] Create LINE Notify channel: https://notify-bot.line.me/
- [ ] Get notification token
- [ ] Add `LINE_NOTIFY_TOKEN` to Railway environment variables
- [ ] Add detection code to `handle_message()`
- [ ] Test with "talk to operator" message
- [ ] Verify operators receive notification

### Week 2: Detection Rules
- [ ] Add medical/legal keyword detection
- [ ] Add repeated question detection
- [ ] Add order issue detection
- [ ] Test each scenario

### Week 3: Error Monitoring
- [ ] Add try-catch around Claude API calls
- [ ] Add try-catch around Google Sheets calls
- [ ] Test error scenarios
- [ ] Verify operators notified

---

## 6. ALTERNATIVE: Webhook to Slack (if operators use Slack)

```python
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

def notify_operator_slack(user_id, issue_type, message):
    payload = {
        "text": f"🚨 Customer Needs Help!\n\nUser: {user_id}\nIssue: {issue_type}\nMessage: {message}",
        "channel": "#customer-support"
    }
    requests.post(SLACK_WEBHOOK_URL, json=payload)
```

---

## 7. METRICS TO TRACK

Add to Google Sheets "Operator_Handoffs" tab:

| Timestamp | User_ID | Issue_Type | Operator | Resolution_Time | Resolved |
|-----------|---------|------------|----------|-----------------|----------|
| 2026-07-15 14:30 | U1234... | EXPLICIT_REQUEST | Jimmy | 5 min | ✅ |
| 2026-07-15 15:45 | U5678... | ORDER_ISSUE | Staff | 12 min | ✅ |

Track:
- How many handoffs per day?
- Which issues trigger most handoffs?
- Average resolution time?
- Customer satisfaction after handoff?

---

## 8. COST SUMMARY

| Method | Setup Time | Monthly Cost | Pros |
|--------|-----------|--------------|------|
| **LINE Notify** | 10 min | FREE | ✅ Instant, easy, operators already on LINE |
| LINE Chat Mode | 30 min | FREE | ✅ Direct chat, full history |
| Email | 15 min | FREE | ✅ Audit trail |
| Slack Webhook | 10 min | FREE | Only if team uses Slack |

**TOTAL COST:** $0/month 🎉

---

## SUMMARY

**Recommended Approach:**
1. **LINE Notify** for instant operator notifications
2. **Automatic detection** of customer issues
3. **Manual handoff** via LINE Official Account Manager
4. **Track metrics** in Google Sheets

**Timeline:**
- Week 1: Basic LINE Notify (2 hours)
- Week 2: Detection rules (4 hours)
- Week 3: Error monitoring (2 hours)

**Total effort:** ~8 hours of development

**Result:** Operators get instant notifications when customers need help, can respond within minutes, all for $0/month!
