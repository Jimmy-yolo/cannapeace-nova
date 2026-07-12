# Local Development Guide

## Quick Start (5 minutes)

### 1. Install Dependencies

```bash
cd /Users/jimmy/repos/cannapeace-nova/demos/restaurant-line-to-excel
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

```bash
cp .env.example .env
# Edit .env with your credentials
```

### 3. Start Local Server

```bash
python app.py
```

Server runs on http://localhost:8001

### 4. Expose to LINE (Choose One)

#### Option A: ngrok (Quick)

```bash
# Install
npm install -g ngrok

# Start tunnel
ngrok http 8001

# Copy HTTPS URL (e.g., https://abc123.ngrok.io)
# Update LINE webhook: https://abc123.ngrok.io/webhook
```

#### Option B: Cloudflare Tunnel (Stable, Free)

```bash
# Install
brew install cloudflare/cloudflare/cloudflared

# Start tunnel
cloudflared tunnel --url http://localhost:8001

# Copy HTTPS URL (e.g., https://xyz.trycloudflare.com)
# Update LINE webhook: https://xyz.trycloudflare.com/webhook
```

### 5. Configure LINE Webhook

1. Go to https://developers.line.biz/console/
2. Select your channel
3. Go to "Messaging API" tab
4. Update Webhook URL with ngrok/Cloudflare URL
5. Click "Verify" (should show "Success")
6. Enable "Use webhook"

### 6. Test

Send a message to your LINE bot!

---

## Development Workflow

### Normal Development

```bash
# Terminal 1: Run app
python app.py

# Terminal 2: Run ngrok/cloudflare tunnel
ngrok http 8001
# OR
cloudflared tunnel --url http://localhost:8001
```

### Debug with ngrok Inspector

Open http://localhost:4040 to see all webhook requests in real-time.

### Test Locally Without LINE

```bash
# Open in browser
open http://localhost:8001

# Or use curl
curl -X POST http://localhost:8001/parse \
  -H "Content-Type: application/json" \
  -d '{"message": "สั่ง ไทยสติ๊ก 5 กรัม"}'
```

---

## Google Sheets Setup

### Option 1: Use File (Local Dev)

1. Place `credentials.json` in this directory
2. In `.env` set: `GOOGLE_CREDENTIALS_PATH=credentials.json`

### Option 2: Use Base64 (Production)

```bash
# Encode credentials
base64 -i credentials.json > credentials_base64.txt

# Copy content and add to .env
GOOGLE_CREDENTIALS_BASE64=<paste here>
```

---

## Common Issues

### "Invalid signature" error
- Check LINE_CHANNEL_SECRET matches your channel
- Verify webhook signature validation is working

### "Can't connect to Claude"
- Check ANTHROPIC_API_KEY is set correctly
- Verify API key is active

### "Google Sheets permission denied"
- Make sure sheet is shared with service account email
- Check GOOGLE_SHEET_ID is correct

### ngrok URL changes on restart
- Use paid ngrok plan for stable URLs ($8/month)
- OR use Cloudflare Tunnel (free stable URLs)

---

## File Structure

```
.
├── app.py                    # Main application
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (gitignored)
├── .env.example             # Template for .env
├── credentials.json         # Google service account (gitignored)
├── customer_config.json     # Product catalog
├── sample_orders.json       # Test data
└── LOCAL_DEV_GUIDE.md       # This file
```

---

## Deploying to Railway

After local testing:

```bash
git add .
git commit -m "feat: Your feature description"
git push origin main
```

Railway auto-deploys on push.

---

## Pro Tips

1. **Keep ngrok running** - Don't restart unless necessary (URL changes)
2. **Use .env for secrets** - Never commit credentials
3. **Test parse endpoint** - Use http://localhost:8001 for quick tests
4. **Watch logs** - Terminal shows all errors in real-time
5. **ngrok inspector** - Best tool for debugging webhooks
