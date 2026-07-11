# Instructions for Claude Code

## Session Startup Protocol

**REQUIRED READING** at start of every session:
1. `CURRENT_RULINGS.md` - Standing law and current state
2. `SHARED_MEMORY.md` - Project history and key decisions
3. Latest Howard directive (if provided)

**REQUIRED FORMAT** for first response:
```
ACK <directive-id>
```

Example: `ACK 2026-07-11-J`

## Validation Rules

**Reports contradicting CURRENT_RULINGS.md are VOID.**

Before reporting MITM results:
- ✅ Use numbers from `C5_1X_RESULTS_TABLE.md` (canonical source)
- ❌ Do NOT use 3x numbers from old txt files
- ❌ Do NOT use retired lockbox txt files
- ✅ Confirm leverage = 1x
- ✅ Confirm window if out-of-sample validation

## Evidence Standard

**DONE = evidence attached**

Acceptable evidence:
- Screenshots
- Log files
- Data tables
- Git commits
- Railway deployment URLs

NOT acceptable:
- Summaries without artifacts
- "I checked and it works"
- Promises to do later

## Credential Security

**PERMANENT RULE:**
- Credentials NEVER appear in responses, reports, commits, docs
- Reference by name and location only
- Example: "LINE_CHANNEL_SECRET in Railway env vars"
- See `CREDENTIALS_README.md` for locations

## Priority Arbitration

1. NOVA paying-customer work
2. MOON research
3. All else

NOVA work preempts MOON work.

---

**Last updated:** 2026-07-11
**Authority:** HOWARD MASTER DIRECTIVE 2026-07-11-J
