# DELIVERY PLAYBOOK — CannaPeace NOVA

**Target:** Small Thai/Chinese businesses needing automation (LINE bots, document translation, order management)
**Per:** DIRECTIVE 2026-07-09-H / P1d (TRACK_A §5 principles)
**Last updated:** 2026-07-09

---

## Quoting & Pricing

**Rule:** Quote = Estimate × 2, minimum 1 week

| Project Type | Estimate | Quote Range | Rationale |
|--------------|----------|-------------|-----------|
| Simple LINE bot (parse orders) | 2-3 days | 1-2 weeks | Integration debugging, customer credential setup |
| Document translator (OCR + PDF) | 3-4 days | 1.5-2 weeks | API stability, multilingual edge cases |
| Custom integration (Sheets + LINE + Thai/Chinese) | 5-7 days | 2-3 weeks | Unknown requirements, iterative refinement |

**Minimum:** 1 week (even for "simple" tasks) - customer credential gathering alone takes 2-3 days

**Payment terms:**
- 50% upfront (before work starts)
- 50% on delivery (after acceptance test passes)
- No work begins without deposit

---

## Scope Template (One-Page, Copy-Paste for Each Customer)

```
=== PROJECT SCOPE: [Customer Name] — [Product Name] ===

WHAT WE'RE BUILDING:
• [One sentence: e.g., "LINE bot that parses Thai restaurant orders and appends to Google Sheet"]

ACCEPTANCE TEST (Pass = You Pay Final 50%):
• [Specific, measurable test - e.g., "3 consecutive days of real orders, ≥90% parse accuracy, daily summary on time"]

WHAT YOU PROVIDE (Deadline: [Date]):
1. LINE Official Account credentials (Channel Secret, Access Token)
2. Google Sheet ID (with edit permissions for service account email we send)
3. Sample order messages (≥10 real examples in Thai/Chinese/English)
4. Menu items list (for validation)

WHAT WE DELIVER (By [Date]):
1. Working bot deployed to Railway/Render (or your hosting)
2. 2 weeks of hand-holding support (bugfixes, tweaks)
3. README with setup instructions for future maintenance

OUT OF SCOPE:
• Multi-language expansion beyond Thai/Chinese/English
• Historical order migration
• Integration with accounting software
• Mobile app development

PRICE: ฿[Amount] THB
• 50% now: ฿[Half]
• 50% on passing acceptance test: ฿[Half]

TIMELINE: [Start Date] → [Delivery Date] (X weeks)

SIGNATURE: _______________  DATE: ___________
```

---

## Founding-Pilot Framing (Say This to First 3 Customers)

**Discount positioning:**
> "You're one of our first 3 pilot customers. Normally this would be ฿30,000, but we're offering ฿15,000 for founding pilots. In exchange, we'd appreciate:
>
> 1. Your patience during our 2-week hand-holding period (we'll fix any bugs same-day)
> 2. A brief testimonial if you're happy with the result
> 3. Permission to use your use-case (anonymized) as a case study
>
> This discount buys you 2 weeks of intensive support, said openly. After that, we can discuss ongoing support contracts."

**Why this works:**
- Frames discount as "pilot program" (not desperation)
- Sets expectation of hand-holding (you're allowed to be responsive)
- Gets testimonials early (social proof for customer #4+)
- Explicit time-box on free support (prevents scope creep)

---

## Support Model

**Included (first 2 weeks after delivery):**
- Bugfixes (parsing errors, bot crashes)
- Minor tweaks (adjust thresholds, add menu items)
- Same-day response to critical issues

**NOT included (after 2 weeks):**
- New features (e.g., "can you add inventory tracking?")
- Integration with new systems
- Performance optimization beyond original scope

**Ongoing support (after 2 weeks):**
- ฿5,000/month retainer: Bugfixes + minor tweaks + monthly check-in
- ฿500/hour for new features (4-hour minimum)
- OR: "Call us when you need something, we'll quote then"

---

## Red Flags (When to Say No)

**Reject if customer:**
1. **Asks for free trial first** → "We offer founding-pilot pricing, but no work without deposit"
2. **Wants unlimited revisions** → "Acceptance test is the finish line. Scope changes = new quote."
3. **Has no budget clarity** → "Our minimum is ฿15,000 for pilots. If that's outside your range, we can revisit in 6 months."
4. **Wants it "by tomorrow"** → "Our minimum timeline is 1 week, even for simple bots. We can start Monday."
5. **Vague requirements** → "Let's define the acceptance test first. Once we know what 'done' looks like, we can quote."

**Good customers:**
- Have budget (ask "how much?" not "can you do it free?")
- Have specific pain point (not "exploring automation")
- Respond to credential requests within 48h
- Understand software takes time

---

## Delivery Checklist (Before Asking for Final 50%)

**Run this checklist AS YOU GO, not at the end:**

- [ ] **Acceptance test passes** (run with customer watching via screen share)
- [ ] **Deployed to production** (not localhost, not your laptop)
- [ ] **Credentials secured** (customer's tokens in their own `.env`, not hardcoded)
- [ ] **README written** (copy template below, fill in blanks)
- [ ] **Handoff session scheduled** (30min walkthrough: "here's how to restart if it breaks")

**README template:**
```markdown
# [Product Name] — Setup & Maintenance

## What This Does
[One sentence from scope doc]

## Hosted At
- URL: https://[app-name].railway.app
- Logs: [Link to Railway logs or your monitoring]

## If It Stops Working
1. Check Railway dashboard: [link]
2. Restart service (click "Restart")
3. If still broken, email: hello@cannapeace.com (response within 24h)

## Credentials (Your Responsibility)
- LINE: Stored in Railway environment variables
- Google Sheets: Service account email is [email@...]
- DO NOT share these with anyone

## Support
- **First 2 weeks (until [Date]):** Included, same-day response
- **After:** ฿5,000/month retainer OR pay-per-incident

## Common Issues
- "Bot not responding" → Check LINE webhook URL is https://[your-app].railway.app/webhook
- "Orders not appearing in sheet" → Verify sheet ID matches `.env` file
```

---

## Multi-Customer Pitfalls (What NOT to Do)

**Per DIRECTIVE P1e:**
- ❌ **No shared platform** — Each customer gets their own Railway instance, their own code repo
- ❌ **No multi-tenant database** — Each customer = isolated deployment
- ❌ **No "CannaPeace Platform v2" before delivery #3** — Common-code extraction happens AFTER 3rd delivery, not before 1st

**Why:**
- Shared infra = one customer's bug breaks everyone
- Multi-tenant = security nightmare for first 3 customers
- Platform thinking = never ship (focus on delivering, not architecting)

**When to extract common code:** After delivery #3, when you see the pattern. Not before.

---

## Customer Zero Rehearsal (Internal Test Before First Real Customer)

**Per P1b (1-day timebox):**

Before approaching first paying customer, run **Restaurant Zero** end-to-end with Jimmy's own LINE + sample menu:

1. **Spin up fresh LINE OA** (test account, not production)
2. **Deploy to Railway** (from scratch, time it)
3. **Test full flow:** LINE message → webhook → Sheet → daily summary
4. **Write INSTALL_CHECKLIST.md** AS YOU GO (every step, every credential, time each step)
5. **Write FRICTION_LOG.md** — Every point where you got stuck, every "wait, where's that setting?" moment

**Output:** INSTALL_CHECKLIST v1 (the real playbook for customer #1)

**Top-5 fixes ranked by:** "Which friction point would break a real install?"

---

## Success Metrics (First 3 Deliveries)

**Green flags:**
- Customer pays final 50% without complaint
- Acceptance test passes on first try
- < 5 support tickets in first 2 weeks
- Customer refers someone else

**Yellow flags:**
- Acceptance test takes >3 attempts to pass
- 5-10 support tickets in first 2 weeks
- Customer asks for scope expansion during handoff

**Red flags:**
- Customer refuses to pay final 50%
- Acceptance test still failing after 1 week
- >10 support tickets in first 2 weeks
- You're doing free work past 2-week window

**Action on red flags:**
1. Stop working immediately
2. Schedule call with customer: "Let's revisit the scope"
3. If unresolved, write off the project (learn from it, don't chase bad money)

---

## Recap: The NOVA Delivery Formula

1. **Quote = Estimate × 2** (always, no exceptions)
2. **50% upfront** (no deposit = no start)
3. **Acceptance test in scope doc** (both parties know "done" before starting)
4. **Founding-pilot discount** (frames discount as pilot program, not desperation)
5. **2 weeks included support** (time-boxed, explicit)
6. **No shared infra before delivery #3** (ship first, architect later)
7. **README + handoff session** (customer can maintain without you)

**One sentence:** Charge enough to care, deliver fast enough to learn, support long enough to fix, then move to next customer.

---

**Next customer:** After Restaurant Zero passes internal rehearsal (P1b)
**Playbook review:** After delivery #3 (update pricing, refine scope template, extract common code)
