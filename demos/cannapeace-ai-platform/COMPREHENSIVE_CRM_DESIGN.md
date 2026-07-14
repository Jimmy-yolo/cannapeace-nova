# Comprehensive CRM Data Model - Complete Customer Intelligence

**Date:** 2026-07-14
**Purpose:** Capture EVERYTHING about customers for personalized service

---

## Customer Data Categories

### 1. Contact Information
**Purpose:** How to reach customer, where to deliver

| Field | Description | Example | Auto-Capture Pattern |
|-------|-------------|---------|---------------------|
| **LINE_User_ID** | Unique identifier | U1234567890 | Automatic |
| **Phone** | Primary contact | 092-343-2606 | "เบอร์ 092-343-2606" |
| **Name** | Customer name | Jimmy | "ชื่อ จิมมี่" |
| **Address** | Delivery address | Bangkok Sukhumvit 11 | "ที่อยู่...", "deliver to..." |
| **Preferred_Contact_Time** | Best time to contact | Evening (18:00-21:00) | "call me after 6pm" |
| **Language_Preference** | Thai/English | Thai | Detect from messages |

### 2. Medical & Usage Information
**Purpose:** Understand customer's needs for better recommendations

| Field | Description | Example | Auto-Capture Pattern |
|-------|-------------|---------|---------------------|
| **Medical_Conditions** | Health issues to address | Insomnia, Chronic pain | "I have insomnia", "ปวดหลัง" |
| **Symptoms** | What they want to treat | Pain, Stress, Sleep issues | "can't sleep", "ปวด", "stress" |
| **Usage_Goal** | Why they use cannabis | Medical, Recreational, Both | "for pain relief", "to relax" |
| **Experience_Level** | Beginner/Intermediate/Expert | Beginner | "first time", "new to cannabis" |
| **Preferred_Effects** | Desired effects | Relaxing, Energizing, Focus | "want to relax", "need energy" |
| **THC_Tolerance** | Low/Medium/High | Low | "I'm sensitive", "high tolerance" |

### 3. Strain & Product Preferences
**Purpose:** Personalize recommendations based on what they love

| Field | Description | Example | Auto-Capture Pattern |
|-------|-------------|---------|---------------------|
| **Favorite_Strains** | Strains they loved | Cap Junky, Gogurtz | From order history + "I love..." |
| **Strain_Type_Pref** | Indica/Sativa/Hybrid | Indica | "prefer indica", "ชอบ indica" |
| **Flavor_Preferences** | Taste preferences | Sweet, Fruity, Earthy | "like fruity flavors" |
| **Avoided_Strains** | What they don't like | None | "didn't like...", "too strong" |
| **Price_Range** | Budget per order | 1000-2000฿ | "budget is 1500฿" |

### 4. Purchase Behavior
**Purpose:** Predict needs, optimize inventory

| Field | Description | Example | Auto-Capture Pattern |
|-------|-------------|---------|---------------------|
| **Typical_Order_Size** | Usual quantity | 5-10g | Average from order history |
| **Order_Frequency** | How often they order | Weekly, Monthly | Calculate from dates |
| **Last_Order_Date** | Most recent order | 2026-07-10 | From Orders sheet |
| **Average_Order_Value** | Typical spending | 800฿ | Calculate from orders |
| **Preferred_Delivery_Day** | Best day for delivery | Saturday | "deliver on weekends" |
| **Preferred_Delivery_Time** | Best time window | Afternoon | "after 2pm" |

### 5. Customer Journey & Engagement
**Purpose:** Know where they are in their journey

| Field | Description | Example | Auto-Capture Pattern |
|-------|-------------|---------|---------------------|
| **Current_Journey_Stage** | Where in funnel | Product Question | AI detection |
| **Acquisition_Source** | How they found us | TikTok Food Account | UTM parameters |
| **First_Seen** | First contact date | 2026-07-01 | Automatic |
| **Last_Seen** | Last interaction | 2026-07-14 | Update on every message |
| **Total_Messages** | Conversation count | 45 | Count from Messages sheet |
| **Total_Orders** | Number of orders | 3 | Count from Orders sheet |
| **Lifetime_Value** | Total spent | 2400฿ | Sum from Orders sheet |

### 6. Segmentation & Flags
**Purpose:** Targeted marketing and VIP treatment

| Field | Description | Example | Auto-Capture Pattern |
|-------|-------------|---------|---------------------|
| **Segment** | Customer type | VIP, Repeat, New | Auto-calculate |
| **VIP_Status** | Is VIP customer | Yes/No | LTV > 10,000฿ |
| **At_Risk** | Hasn't ordered recently | Yes/No | >30 days since last order |
| **Tags** | Custom labels | Medical, High-roller, Picky | Manual + auto |
| **Notes** | Special instructions | Allergic to citrus | Manual entry |
| **Referral_Source** | Who referred them | Friend: @user123 | "friend told me" |

---

## Expanded Customers Sheet Structure (30 columns!)

```
A. LINE_User_ID
B. Phone
C. Name
D. Address
E. Preferred_Contact_Time
F. Language_Preference

G. Medical_Conditions
H. Symptoms
I. Usage_Goal
J. Experience_Level
K. Preferred_Effects
L. THC_Tolerance

M. Favorite_Strains
N. Strain_Type_Pref
O. Flavor_Preferences
P. Avoided_Strains
Q. Price_Range

R. Typical_Order_Size
S. Order_Frequency
T. Last_Order_Date
U. Average_Order_Value
V. Preferred_Delivery_Day
W. Preferred_Delivery_Time

X. Current_Journey_Stage
Y. Acquisition_Source
Z. First_Seen
AA. Last_Seen
AB. Total_Messages
AC. Total_Orders
AD. Lifetime_Value

AE. Segment
AF. VIP_Status
AG. At_Risk
AH. Tags
AI. Notes
```

---

## Smart Extraction Patterns (Comprehensive)

### Contact Info
```python
phone_patterns = [
    r'(?:เบอร์|โทร|เบอ|phone|tel)[:\s]*([0-9\-]{9,12})',
    r'([0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{4})',
]

name_patterns = [
    r'(?:my name is|i\'?m|ชื่อ)[:\s]+([ก-๙a-zA-Z\s]{2,30})',
]

address_patterns = [
    r'(?:address|ที่อยู่|deliver to|ส่งที่)[:\s]+(.{10,100})',
    r'(bangkok|กรุงเทพ|สุขุมวิท|sukhumvit).{5,80}',
]
```

### Medical & Usage
```python
medical_patterns = [
    r'(?:I have|มี)[:\s]+(insomnia|pain|anxiety|depression|ปวด|นอนไม่หลับ)',
    r'(?:suffer from|เป็น)[:\s]+(.{5,50})',
]

symptoms_patterns = [
    r'(?:can\'?t sleep|sleep problem|นอนไม่หลับ)',
    r'(?:chronic pain|ปวดเรื้อรัง)',
    r'(?:stress|เครียด|anxiety|กังวล)',
]

usage_goal_patterns = [
    r'(?:for|เพื่อ)[:\s]+(pain relief|relaxation|sleep|recreation)',
    r'(?:medical|recreational|both)',
]
```

### Preferences
```python
strain_pref_patterns = [
    r'(?:prefer|like|love|ชอบ)[:\s]+(indica|sativa|hybrid)',
    r'(?:favorite strain|ชอบสายพันธุ์)[:\s]+([a-zA-Z\s]{3,30})',
]

effect_pref_patterns = [
    r'(?:want to|need to|ต้องการ)[:\s]+(relax|energize|focus|sleep|ผ่อนคลาย)',
    r'(?:looking for)[:\s]+(relaxing|energizing|uplifting)',
]

flavor_pref_patterns = [
    r'(?:like|prefer|ชอบ)[:\s]+(sweet|fruity|earthy|citrus|กลิ่น)',
]
```

### Behavior
```python
budget_patterns = [
    r'(?:budget|งบ)[:\s]*([0-9,]{3,6})',
    r'(?:around|ประมาณ)[:\s]*([0-9,]{3,6})',
]

frequency_patterns = [
    r'(?:order|สั่ง)[:\s]+(every week|weekly|monthly|ทุกสัปดาห์|ทุกเดือน)',
]

delivery_time_patterns = [
    r'(?:deliver|ส่ง)[:\s]+(morning|afternoon|evening|weekend|เช้า|บ่าย|เย็น)',
    r'(?:after|หลัง)[:\s]+([0-9]{1,2})\s*(?:pm|โมง)',
]
```

---

## AI-Assisted Extraction Strategy

Instead of relying only on regex, use **Claude AI** to extract structured data:

```python
async def extract_all_customer_info_with_ai(conversation_history):
    """
    Use Claude to analyze entire conversation and extract ALL customer info
    """

    prompt = f"""Analyze this customer conversation and extract ALL available information.

Conversation history:
{conversation_history}

Extract and return ONLY what is explicitly mentioned (no assumptions):

{{
    "contact": {{
        "phone": "xxx-xxx-xxxx or null",
        "name": "name or null",
        "address": "full address or null"
    }},
    "medical": {{
        "conditions": ["list of conditions or []"],
        "symptoms": ["list of symptoms or []"],
        "usage_goal": "medical/recreational/both or null"
    }},
    "preferences": {{
        "favorite_strains": ["strain names or []"],
        "strain_type": "indica/sativa/hybrid or null",
        "effects": ["desired effects or []"],
        "flavors": ["flavor preferences or []"]
    }},
    "behavior": {{
        "budget_range": "min-max or null",
        "order_frequency": "frequency or null",
        "delivery_preference": "time preference or null"
    }}
}}

Return ONLY valid JSON."""

    response = await anthropic_client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    return json.loads(response.content[0].text)
```

---

## When to Update Profile

### 1. On Every Message (Light)
- Update Last_Seen
- Increment Total_Messages
- Quick regex scan for phone/name/address

### 2. Every 5 Messages (Moderate)
- Run AI extraction on last 10 messages
- Update medical info, preferences
- Enrich profile with new insights

### 3. After Order Completion (Full)
- Update all purchase behavior fields
- Recalculate segment, VIP status
- Update favorite strains from order
- Check if at-risk status changes

### 4. Weekly Batch (Analytics)
- Calculate order_frequency for all customers
- Update at-risk flags (>30 days)
- Recalculate average_order_value
- Generate insights

---

## Personalization Use Cases

### 1. Smart Recommendations
```
Customer profile shows:
- Symptoms: Insomnia
- Preferred_Effects: Relaxing
- Strain_Type_Pref: Indica
- Flavor_Preferences: Sweet

→ Bot recommends: Gogurtz (Indica, Sweet, Relaxing)
```

### 2. VIP Treatment
```
Customer profile shows:
- Segment: VIP
- Lifetime_Value: 15,000฿
- Total_Orders: 12

→ Bot offers: "Welcome back! As a VIP, you get 10% off today 🌟"
```

### 3. Re-engagement
```
Customer profile shows:
- Last_Order_Date: 45 days ago
- At_Risk: Yes
- Favorite_Strains: Cap Junky

→ Automated message: "Hi! We miss you 💚 Cap Junky is back in stock!"
```

### 4. Medical Support
```
Customer profile shows:
- Medical_Conditions: Chronic Pain
- THC_Tolerance: Low
- Experience_Level: Beginner

→ Bot suggests: Lower THC options, CBD-rich strains, dosing guidance
```

---

## Implementation Phases

### Phase 1: Expand Schema (Today)
- Add 30 columns to Customers sheet
- Migrate existing data
- Test basic writes

### Phase 2: Smart Extraction (Week 2)
- Implement comprehensive regex patterns
- Add AI-assisted extraction
- Test on real conversations

### Phase 3: Personalization (Week 3)
- Update Claude prompt with profile data
- Implement smart recommendations
- Add VIP detection and treatment

### Phase 4: Automation (Week 4)
- Auto re-engagement for at-risk customers
- Weekly analytics batch job
- Insights dashboard

---

## Success Metrics

After implementing comprehensive CRM:

✅ **95%+ data capture rate** (vs 20% with forms)
✅ **Zero friction** - customers just chat naturally
✅ **Personalized recommendations** based on full profile
✅ **VIP detection** and special treatment
✅ **Medical support** for customers with conditions
✅ **Predictive insights** (who will order next, who's at risk)

---

## Summary

**Old Way (Piecemeal):**
- Capture phone ✓
- Capture name ✓
- Miss everything else ✗

**New Way (Comprehensive):**
- 30 data points per customer
- Medical info → Better recommendations
- Preferences → Personalization
- Behavior → Predictive analytics
- All automatic from conversation!

**Next:** Implement Phase 1 (expand schema) right now!

---

**This is how we build a REAL CRM that actually understands customers.** 🚀
