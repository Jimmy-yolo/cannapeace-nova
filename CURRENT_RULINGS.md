# Current Rulings - MOON Project

**Last updated:** 2026-07-11 (Directive 2026-07-11-J)

## Standing Law

### Leverage
- **LOCKED at 1x** (ADR-002/D3)
- No 3x testing permitted
- All results must use 1x leverage

### LOCKBOX Window
- **2026-01-08 → 2026-07-08 = SPENT**
- See LOCKBOX.md for methodology
- This window cannot be reused for validation
- 6+ validation queries already run on this period

### MITM Strategy Status
- **Status:** HYPOTHESIS at 1x leverage
- **Canonical numbers:** C5_1X_RESULTS_TABLE.md
  - SOL: +10.19% | Sharpe 0.89 | DD 7.6%
  - LINK: +7.42% | Sharpe 0.69 | DD 5.7%
- **NOT** the 3x txt files (those are void)
- **NOT** the lockbox txt files (those were 3x runs, retired)

### Pair Restrictions
- **No new pairs** on the spent lockbox window
- Current approved pairs: SOL/USDT:USDT, LINK/USDT:USDT
- Additional pairs require new out-of-sample data

### Dry-Run Requirements
- **Minimum duration:** 4-8 weeks
- **Execution fidelity criteria:** per RUNBOOK
- **Returns:** recorded not judged until ≥12 weeks OR ≥50 trades
- **Monitoring:** FreqUI + logs + daily review

### Arbitration Priority
1. NOVA paying-customer work
2. MOON research
3. All else

### Evidence Standard
- **DONE = evidence attached**
- Screenshots, logs, or data files required
- No summaries without artifacts

### Credential Security
- **Credentials NEVER** appear in reports, chats, commits, or docs
- Reference by name and location only
- See CREDENTIALS_README.md for locations
- Violations = immediate halt and scrub

---

## Session Continuity Protocol

Before each session, read:
1. This file (CURRENT_RULINGS.md)
2. SHARED_MEMORY.md
3. Latest Howard directive

First line of every report: `ACK <directive-id>`

Reports contradicting this file are **VOID**.

---

**Effective:** 2026-07-11
**Authority:** HOWARD MASTER DIRECTIVE 2026-07-11-J
