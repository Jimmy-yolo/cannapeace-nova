# Deployment Requirements — D1 Thai-Chinese Translator

**Railway Deployment:** 30-minute timebox per N2 directive

---

## Required from Jimmy

### 1. OpenAI API Key
**Variable:** `OPENAI_API_KEY`
**Format:** `sk-proj-...`
**Purpose:** GPT-4 translation (Chinese → Thai)
**Fallback:** Sample data if not provided (DEMO MODE)

### 2. Google Cloud Vision Credentials
**Variable:** `GOOGLE_APPLICATION_CREDENTIALS`
**Format:** Path to JSON file OR base64-encoded JSON
**Purpose:** OCR for Chinese text extraction
**Fallback:** Sample Chinese text if not provided (DEMO MODE)

**Credential file structure:**
```json
{
  "type": "service_account",
  "project_id": "...",
  "private_key_id": "...",
  "private_key": "...",
  "client_email": "...",
  ...
}
```

---

## Railway Setup Steps (30 min)

1. Create new Railway project
2. Connect GitHub repo: `Jimmy-yolo/cannapeace-nova`
3. Set root directory: `demos/thai-chinese-translator`
4. Add environment variables:
   - `OPENAI_API_KEY=sk-proj-...`
   - `GOOGLE_APPLICATION_CREDENTIALS` (base64 encode the JSON file)
5. Deploy
6. Get public URL
7. Test with smoke_test.md

---

## Without API Keys (DEMO MODE)

Demo will work with sample data:
- OCR: Returns hardcoded sample Chinese invoice text
- Translation: Returns hardcoded Thai translation
- PDF: Generates bilingual PDF from sample data
- UI: Shows "DEMO MODE" warning banner

**Good for:** Testing deployment, UI flow verification
**Not good for:** Live demos with prospect's own documents
