# FRICTION_LOG — Restaurant LINE-to-Excel (Customer Zero)

**Per:** DELIVERY_PLAYBOOK P1b (Customer Zero rehearsal)
**Purpose:** Document EVERY point where install got stuck, confused, or slowed down
**Date:** 2026-07-10
**Customer:** [Restaurant Zero - Internal Test]

---

## How to Use This Log

**During installation, record:**
1. **What you were trying to do** (step from INSTALL_CHECKLIST)
2. **What went wrong** (error, confusion, missing info)
3. **How long it took to fix** (actual time, not estimate)
4. **What the fix was**
5. **Severity:** Low (cosmetic) / Medium (delays install) / High (blocks install)

**After installation:**
- Rank all friction points by severity
- Identify top-5 fixes for customer #2
- Update INSTALL_CHECKLIST with better instructions

---

## Friction Points (Recorded During Install)

### Friction #1: [TITLE]

**Step:** [Which INSTALL_CHECKLIST step]
**What went wrong:**
- [Describe the issue]

**Time lost:** [X minutes]

**Root cause:**
- [ ] Missing documentation
- [ ] Customer confusion
- [ ] Tool/API issue
- [ ] Our code bug
- [ ] Environment problem
- [ ] Other: ___________

**Fix applied:**
- [How we solved it]

**Severity:** Low / Medium / High

**Prevention for next install:**
- [What to change in INSTALL_CHECKLIST or code]

---

### Friction #2: [TITLE]

**Step:**
**What went wrong:**
**Time lost:**
**Root cause:**
**Fix applied:**
**Severity:**
**Prevention:**

---

### Friction #3: [TITLE]

**Step:**
**What went wrong:**
**Time lost:**
**Root cause:**
**Fix applied:**
**Severity:**
**Prevention:**

---

### Friction #4: [TITLE]

**Step:**
**What went wrong:**
**Time lost:**
**Root cause:**
**Fix applied:**
**Severity:**
**Prevention:**

---

### Friction #5: [TITLE]

**Step:**
**What went wrong:**
**Time lost:**
**Root cause:**
**Fix applied:**
**Severity:**
**Prevention:**

---

## Expected vs Actual Timeline

| Phase | Expected Time | Actual Time | Delta | Notes |
|-------|---------------|-------------|-------|-------|
| Pre-deployment (customer prep) | 2-3 days | | | |
| Local environment setup | 15-20 min | | | |
| Configuration | 10-15 min | | | |
| Local testing | 10-15 min | | | |
| Railway deployment | 20-25 min | | | |
| LINE webhook config | 5-10 min | | | |
| End-to-end test | 10-15 min | | | |
| Customer handoff | 30 min | | | |
| **TOTAL (Active Work)** | **1.5-2 hours** | | | |

---

## Top-5 Fixes for Customer #2

**Ranked by:** Impact × Frequency × Fix Difficulty

1. **[FIX #1]**
   - **Problem:** [Issue that blocked/delayed install]
   - **Solution:** [What to change]
   - **Impact:** Saves X minutes per install
   - **Implementation:** [Code change / doc update / tool change]

2. **[FIX #2]**
   - **Problem:**
   - **Solution:**
   - **Impact:**
   - **Implementation:**

3. **[FIX #3]**
   - **Problem:**
   - **Solution:**
   - **Impact:**
   - **Implementation:**

4. **[FIX #4]**
   - **Problem:**
   - **Solution:**
   - **Impact:**
   - **Implementation:**

5. **[FIX #5]**
   - **Problem:**
   - **Solution:**
   - **Impact:**
   - **Implementation:**

---

## Common Patterns Observed

### Pattern: [NAME]

**Occurred in steps:** [List steps where this happened]
**Root cause:** [Why this keeps happening]
**Systematic fix:** [How to prevent this category of issue]

---

### Pattern: [NAME]

**Occurred in steps:**
**Root cause:**
**Systematic fix:**

---

## Customer #2 Checklist Improvements

**Before starting Customer #2 install, apply these changes:**

- [ ] Update INSTALL_CHECKLIST.md with fixes #1-5
- [ ] Add pre-flight check script (verify env before starting)
- [ ] Create credentials template with examples
- [ ] Add troubleshooting section for top 3 errors
- [ ] Record video walkthrough of full install
- [ ] Test install on fresh machine (verify instructions work)

---

## Acceptance Test Results (Customer Zero)

**Pass criteria:** 3 consecutive days, ≥90% parse accuracy, zero downtime

| Day | Orders Sent | Orders Parsed | Parse Accuracy | Bot Uptime | Issues |
|-----|-------------|---------------|----------------|------------|--------|
| Day 1 | | | | | |
| Day 2 | | | | | |
| Day 3 | | | | | |

**Final result:** PASS / FAIL

**If FAIL, blockers:**
- [List issues that prevented passing]

---

## Lessons Learned

### What Worked Well

1. [Something that went smoothly]
2. [Something that saved time]
3. [Something customer understood immediately]

### What Was Difficult

1. [Something that took multiple attempts]
2. [Something that confused us or customer]
3. [Something that required workaround]

### Surprises (Good or Bad)

1. [Unexpected issue or success]
2. [Assumption that was wrong]
3. [Tool that behaved differently than expected]

---

## Next Steps

**Immediate (before Customer #1):**
- [ ] Apply top-5 fixes
- [ ] Update INSTALL_CHECKLIST with actual timings
- [ ] Create pre-flight check script
- [ ] Test on fresh environment

**For Customer #1:**
- Estimated install time: [ACTUAL TIME FROM THIS RUN]
- Confidence level: Low / Medium / High
- Backup plan if install fails: [Plan B]

**For DELIVERY_PLAYBOOK:**
- Update quote formula based on actual time
- Add Customer Zero learnings to red flags section
- Refine acceptance test criteria

---

## Raw Notes (Stream of Consciousness)

**Use this section for quick notes during install:**

[Timestamp] [What happened]
[Timestamp] [What happened]
[Timestamp] [What happened]

**Example:**
```
10:05 - Started local env setup, Python 3.13 not compatible with one package
10:12 - Fixed by downgrading to Python 3.11
10:15 - Venv created, installing deps...
10:18 - pip install failed on google-auth, needed wheel installed first
10:22 - All deps installed, took 7 minutes (expected 3-5)
```

---

## Appendix: Environment Details

**Machine:**
- OS: macOS 14.5 / Ubuntu 22.04 / Windows 11
- Python version: 3.x.x
- pip version: xx.x
- Railway CLI version: x.x.x

**Customer Environment (if different):**
- [Details if testing on customer's machine]

**Network:**
- Internet speed: [Mbps]
- Firewall issues: Yes / No
- VPN active: Yes / No

---

**Installation completed:** [Date/Time]
**Total time (start to handoff):** [X hours Y minutes]
**Installer:** [Your name]
**Customer Zero contact:** [For follow-up questions]
