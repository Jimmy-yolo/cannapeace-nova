# LINE Official Account Staff Management Guide

**For:** CannaPeace operator team (Peter, Jay, James, etc.)

---

## HOW LINE OFFICIAL ACCOUNT STAFF WORKS

### Company-Owned Account ✅
- LINE Official Account = **Company property** (CannaPeace owns it)
- Account: @cannapeace
- Not tied to any individual's personal LINE

### Staff Access via Personal LINE
- Peter, Jay, James each have their **own personal LINE accounts**
- Company admin **invites them** to access @cannapeace Official Account
- They log in with their personal LINE, but manage company account
- When they leave company, admin **removes their access**

---

## SETUP PROCESS

### Step 1: Add Staff Members

**Admin (you) goes to:**
1. https://manager.line.biz/
2. Login with company LINE Official Account
3. Click **Settings** → **Account settings** → **Roles**
4. Click **Invite member**
5. Enter staff's LINE account info (email or LINE ID)
6. Choose role: **Admin** or **Operator**

### Step 2: Staff Accepts Invitation

**Peter/Jay/James receives:**
1. Invitation notification in their personal LINE app
2. They accept invitation
3. Now they can access @cannapeace account

### Step 3: Staff Access Company Account

**When Peter starts work:**
1. Opens LINE app on their phone
2. Switches to **LINE Official Account** mode
3. Selects **@cannapeace** from their account list
4. Now they can see & respond to customer chats
5. All messages sent as "@cannapeace", NOT as Peter personally

**When Peter ends work:**
- Just closes the app or switches back to personal LINE
- No "log off" needed - they just stop responding
- Other staff (Jay) can take over

---

## STAFF ROLES

LINE Official Account has 4 role types:

### 1. **Admin** (Full Access)
**Can do:**
- ✅ Add/remove staff
- ✅ Change account settings
- ✅ Respond to customer chats
- ✅ Send broadcasts
- ✅ View analytics
- ✅ Manage billing

**Recommended for:** Owner (you), Manager

### 2. **Operator** (Chat Only)
**Can do:**
- ✅ Respond to customer chats
- ✅ View chat history
- ✅ Tag chats
- ✅ Add notes
- ❌ Cannot change settings
- ❌ Cannot add/remove staff
- ❌ Cannot send broadcasts

**Recommended for:** Peter, Jay, James (customer service staff)

### 3. **Analyst** (Read-Only)
**Can do:**
- ✅ View analytics
- ✅ Download reports
- ❌ Cannot chat with customers
- ❌ Cannot change settings

**Recommended for:** Marketing team, data analysts

### 4. **Message Manager** (Marketing)
**Can do:**
- ✅ Send broadcasts
- ✅ Create messages
- ❌ Cannot respond to chats
- ❌ Cannot change settings

**Recommended for:** Marketing team (if separate from operations)

---

## RECOMMENDED SETUP FOR CANNAPEACE

### Your Team Structure:

| Person | Role | Access |
|--------|------|--------|
| **You (Owner)** | Admin | Full access - add staff, change settings, billing |
| **Peter** | Operator | Chat with customers, view history, add notes |
| **Jay** | Operator | Chat with customers, view history, add notes |
| **James** | Operator | Chat with customers, view history, add notes |

### Why This Works:
- ✅ Company owns @cannapeace (not tied to individuals)
- ✅ Staff use personal LINE (no company phones needed)
- ✅ You control who has access (add/remove anytime)
- ✅ All chats logged under @cannapeace (not personal accounts)
- ✅ When staff leaves, remove their access (they lose access immediately)
- ✅ Chat history stays with company (doesn't go with staff)

---

## DAILY WORKFLOW

### Morning Shift: Peter Starts Work
1. Peter opens LINE app on his phone
2. Switches to "Official Account" mode
3. Selects "@cannapeace"
4. Sees all customer chats waiting
5. Responds to customers (messages sent as @cannapeace)

### Afternoon Shift: Jay Takes Over
1. Peter finishes shift, closes app (or leaves @cannapeace mode)
2. Jay opens LINE app
3. Switches to "@cannapeace"
4. Sees all chats (including Peter's conversations)
5. Continues helping customers

### Evening: James Covers
1. Jay finishes, James logs in
2. Same process - all chat history visible
3. Seamless handoff

---

## CHAT HANDOFF MODES

LINE Official Account has 3 response modes:

### **Option A: Bot Mode (Current)**
- All messages handled by bot (Claude AI)
- Operators can't respond
- Good for: Automated 24/7 service

### **Option B: Chat Mode**
- All messages go to operators
- Bot doesn't respond
- Operators respond manually
- Good for: High-touch service, complex issues

### **Option C: Module Mode (RECOMMENDED)**
- **Smart routing:**
  - Bot handles most messages automatically
  - Operator can "take over" specific chats when needed
  - Bot resumes after operator finishes
- Good for: Best of both worlds

---

## HOW TO IMPLEMENT MODULE MODE (RECOMMENDED)

### What is Module Mode?
- Bot handles 90% of chats automatically (FREE replies!)
- When customer needs help, operator clicks "Take over chat"
- Operator responds manually (bot pauses for that chat)
- When done, operator clicks "Return to bot"
- Bot resumes automatic responses

### Benefits:
- ✅ Scalable: Bot handles routine questions
- ✅ Human touch: Operators handle complex issues
- ✅ Cost-effective: Most replies are FREE (bot)
- ✅ Better CX: Humans available when needed

### How to Enable:
1. Go to https://manager.line.biz/
2. Settings → Response settings
3. Select **"Module mode"**
4. Configure:
   - Auto-response: **On** (bot handles)
   - Chat: **Available** (operators can take over)
   - Smart reply: **On** (suggested responses for operators)

### Staff Workflow in Module Mode:

**Normal operation:**
- Bot (Claude) handles all chats automatically
- Operators monitor chats in LINE Official Account Manager

**When customer needs help:**
1. Bot detects issue (see OPERATOR_NOTIFICATION_SYSTEM.md)
2. Bot sends notification: "🚨 Customer needs help!"
3. Operator sees notification in LINE Official Account Manager
4. Operator clicks **"Take over chat"**
5. Operator responds manually
6. When done, clicks **"Return to bot"**
7. Bot resumes

---

## ACCESS CONTROL

### Adding New Staff (Peter joins):
1. You (Admin): Settings → Roles → Invite member
2. Enter Peter's email or LINE ID
3. Select role: **Operator**
4. Peter gets invitation in his LINE
5. Peter accepts → Can now access @cannapeace

### Removing Staff (James leaves company):
1. You (Admin): Settings → Roles → Manage members
2. Find James in list
3. Click **Remove**
4. James **immediately loses access** to @cannapeace
5. All chat history **stays with company**

### Security:
- ✅ Each staff member uses their personal LINE (no shared passwords)
- ✅ LINE's 2FA protects their accounts
- ✅ Admin can remove access instantly
- ✅ Audit log shows who responded to which chats
- ✅ No need for company phones (BYOD - Bring Your Own Device)

---

## CHAT ASSIGNMENT & TAGGING

### Assign Chats to Specific Operators:

**Use case:** VIP customer → assign to Peter

1. Operator A sees new chat
2. Clicks **"Assign to..."**
3. Selects **Peter**
4. Peter gets notification
5. Peter handles that customer

### Tag Chats:

**Use case:** Organize by issue type

- Tag: "Order Issue"
- Tag: "Medical Question"
- Tag: "VIP Customer"
- Tag: "Complaint"

Filter chats by tag to prioritize.

---

## MOBILE APP FOR OPERATORS

### LINE Official Account App (FREE)

**Download:**
- iOS: https://apps.apple.com/app/line-official-account/id1446321009
- Android: https://play.google.com/store/apps/details?id=com.linecorp.lineoa

**What staff can do on mobile:**
- ✅ Respond to customer chats
- ✅ View chat history
- ✅ Assign chats to colleagues
- ✅ Add tags & notes
- ✅ See customer profiles
- ✅ Upload images/videos
- ✅ Get push notifications for new chats

**Benefits:**
- Staff can respond from anywhere
- No need to be at computer
- Instant notifications
- Better work-life balance (respond during downtime if urgent)

---

## BEST PRACTICES

### 1. Set Working Hours
In LINE Official Account Manager:
- Settings → Response settings → Working hours
- Set: Mon-Sat 9AM-9PM (example)
- Outside hours: Bot handles (or auto-reply: "We'll respond tomorrow!")

### 2. Create Response Templates
Common questions → save as templates:
- "Delivery time: 1-2 hours"
- "Minimum order: 3 grams"
- "Store address: [link]"

Operators click template → instant response

### 3. Use Smart Reply
LINE suggests responses based on customer message:
- Customer: "What's your address?"
- Smart reply suggests: "[Store address]"
- Operator clicks → sent

### 4. Monitor Response Time
Settings → Analytics → Response time
- Target: < 5 minutes
- Track: Which operators are fastest?
- Improve: Train slower operators

### 5. Handoff Notes
When Peter hands off to Jay:
- Peter adds note: "Customer wants Sativa recommendation, allergic to citrus"
- Jay sees note, continues conversation seamlessly

---

## COST

**LINE Official Account staff access:** FREE

- Add unlimited operators: FREE
- Chat access: FREE
- Mobile app: FREE
- Module mode: FREE
- Chat assignment: FREE
- Tags & notes: FREE

**Only paid features:**
- Broadcast messages (paid)
- API calls (if over quota)

**Estimated cost for CannaPeace:**
- 3 operators (Peter, Jay, James): $0/month
- Module mode (bot + human): $0/month (replies are FREE!)
- **Total: $0/month** 🎉

---

## SETUP CHECKLIST

### Week 1: Basic Setup
- [ ] Go to https://manager.line.biz/
- [ ] Enable Module Mode (Settings → Response settings)
- [ ] Add Peter as Operator (Settings → Roles → Invite)
- [ ] Add Jay as Operator
- [ ] Add James as Operator
- [ ] Install LINE Official Account app on staff phones
- [ ] Test: Send test message, Peter responds

### Week 2: Optimize
- [ ] Create response templates for common questions
- [ ] Set up chat tags (Order Issue, VIP, etc.)
- [ ] Configure working hours
- [ ] Train staff on Module Mode (take over / return to bot)
- [ ] Set response time target (< 5 min)

### Week 3: Monitor
- [ ] Check Analytics → Response time
- [ ] Review which operators handle most chats
- [ ] Identify common issues (create more templates)
- [ ] Adjust bot detection triggers (see OPERATOR_NOTIFICATION_SYSTEM.md)

---

## TROUBLESHOOTING

### "Staff can't see chats"
- Check: Did they accept invitation?
- Check: Settings → Roles → Is their role "Operator"?
- Check: Is Module Mode enabled?

### "Bot and human both responding"
- Solution: Use Module Mode + "Take over chat" feature
- When operator takes over, bot pauses for that chat

### "Customer confused who they're talking to"
- Solution: Operator introduces themselves: "Hi! I'm Peter from CannaPeace. How can I help?"
- Bot messages signed: "[Bot]" or emoji indicator

### "Staff left company, still has access"
- Solution: Settings → Roles → Remove member (immediate effect)

---

## SUMMARY

**LINE Official Account Staff Management:**
- ✅ Company-owned account (@cannapeace)
- ✅ Add unlimited staff (Peter, Jay, James, etc.)
- ✅ Staff use personal LINE (no company phones needed)
- ✅ Admin controls who has access (add/remove anytime)
- ✅ Module Mode = Bot + Human (best of both worlds)
- ✅ Mobile app for operators (respond anywhere)
- ✅ FREE for all features you need
- ✅ Chat history stays with company forever

**Recommended Setup:**
- You: Admin (full access)
- Peter/Jay/James: Operators (chat access only)
- Mode: Module Mode (bot handles most, operators take over when needed)
- App: LINE Official Account mobile app on staff phones

**Cost:** $0/month 🎉

**Setup time:** 2 hours (invite staff, configure Module Mode, train team)

---

Ready to set up? Let me know if you have questions!
