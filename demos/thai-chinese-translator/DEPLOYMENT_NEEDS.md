# Deployment Requirements — D1 Thai-Chinese Translator

**Railway Deployment:** 30-minute timebox per N2 directive

---

## Required from Jimmy

### Anthropic API Key
**Variable:** `ANTHROPIC_API_KEY`
**Format:** `sk-ant-...`
**Purpose:** Claude API for both OCR (vision) and translation (Chinese → Thai)
**Fallback:** Sample data if not provided (DEMO MODE)

**Key capabilities:**
- Claude's vision model reads images directly (multimodal)
- Extracts Chinese text from invoice images
- Translates to Thai with structured output (key fields)
- No need for separate services or credentials

---

## Railway Setup Steps (30 min)

1. Create new Railway project
2. Connect GitHub repo: `Jimmy-yolo/cannapeace-nova`
3. Set root directory: `demos/thai-chinese-translator`
4. Add environment variable:
   - `ANTHROPIC_API_KEY=sk-ant-...`
5. Deploy
6. Get public URL
7. Test with smoke_test.md

---

## Without API Key (DEMO MODE)

Demo will work with sample data:
- OCR: Returns hardcoded sample Chinese invoice text (no image processing needed)
- Translation: Returns hardcoded Thai translation
- PDF: Generates bilingual PDF from sample data
- UI: Shows working flow with demo data

**Good for:** Testing deployment, UI flow verification
**Not good for:** Live demos with prospect's own documents

---

## Environment Variables Summary

| Variable | Required | Example | Purpose |
|----------|----------|---------|---------|
| `ANTHROPIC_API_KEY` | Yes (for live mode) | `sk-ant-api03-...` | Claude API for vision + translation |

**To run in demo mode:** Don't set any environment variables. The app will use hardcoded sample Chinese and Thai text.
