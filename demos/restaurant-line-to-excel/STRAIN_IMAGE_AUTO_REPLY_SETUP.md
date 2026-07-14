# Strain Image Auto-Reply Setup Complete ✅

## What's Been Done

Your LINE bot now has **automatic strain image replies** integrated! When customers ask about a specific strain, the bot will automatically send:
1. A detailed text response with strain information
2. The corresponding high-quality product image from `product_images/v6/`

## Files Updated

### `app.py`
- ✅ Added FastAPI static file serving for strain images
- ✅ Configured `/strain-images/` endpoint to serve PNG files
- ✅ Updated image URL generation to use real product images (not placeholders)
- ✅ Added smart name mapping for strain variations (e.g., "Trop Cherry" → "Tropical Cherry")
- ✅ Added `/strain-images-list` endpoint for testing and debugging

## Available Strain Images

The bot can now send images for these 7 strains:

1. **Alien Marker** (7.38 MB)
2. **Any Day** (7.82 MB)
3. **Apple Banana** (7.37 MB)
4. **Berry Bonds** (7.06 MB)
5. **Gogurtz** (7.09 MB)
6. **Miracle Mints** (6.92 MB)
7. **Tropical Cherry** (7.06 MB)

## How It Works

### Customer Flow
1. Customer sends message: "Tell me about Alien Marker"
2. Bot (Claude AI) recognizes this as a strain query
3. Bot responds with: `SEND_IMAGE:Alien Marker`
4. Code detects the marker and:
   - Finds the image file: `product_images/v6/Alien Marker.png`
   - Generates public URL: `https://your-domain.com/strain-images/Alien%20Marker.png`
   - Sends image via LINE API
   - Sends text description

### Name Variations Handled
- "Trop Cherry" or "Tropical Cherry" → `Tropical Cherry.png`
- "LCG x Grapegas" → Gracefully handled
- "Any Day" → `Any Day.png`
- "Miracle Mints" → `Miracle Mints.png`

## Testing Locally

```bash
# 1. Activate virtual environment
cd /Users/jimmy/CannaPeace/products/nova/demos/restaurant-line-to-excel
source venv/bin/activate

# 2. Start the server
python app.py

# 3. Test endpoints
# List all strain images:
curl http://localhost:8001/strain-images-list

# Access a specific image:
curl http://localhost:8001/strain-images/Alien%20Marker.png -o test.png

# Check health:
curl http://localhost:8001/health
```

## Deploying to Railway

When you deploy to Railway, the images will automatically be served at:
```
https://your-railway-domain.up.railway.app/strain-images/Alien%20Marker.png
```

The code automatically detects Railway's `RAILWAY_PUBLIC_DOMAIN` environment variable and uses it to generate the correct public URLs.

### Important: Environment Variables

Make sure these are set in Railway:
- `LINE_CHANNEL_SECRET` - Your LINE channel secret
- `LINE_CHANNEL_ACCESS_TOKEN` - Your LINE channel access token
- `ANTHROPIC_API_KEY` - Your Claude API key
- `RAILWAY_PUBLIC_DOMAIN` - Auto-set by Railway

Optional (for Google Sheets integration):
- `GOOGLE_CREDENTIALS_BASE64` - Base64-encoded service account JSON
- `GOOGLE_SHEET_ID` - Your Google Sheet ID

## Testing with Real LINE Messages

Once deployed, customers can:

1. **Ask about menu:**
   - Customer: "menu" or "list"
   - Bot: Shows full menu with all 7 strains

2. **Ask about specific strain:**
   - Customer: "Tell me about Gogurtz"
   - Bot: Sends image + detailed description

3. **Place an order:**
   - Customer: "I want 10g of Alien Marker"
   - Bot: Guides through order (asks for phone, address)
   - Order saved to Google Sheet automatically

## Debugging

### Check which images are available:
```bash
ls -la product_images/v6/
```

### View server logs:
When running locally, watch the console for these messages:
- `📸 Sending image for: Alien Marker from https://...`
- `⚠️ Image not found for: ...` (if there's a mismatch)

### Test the auto-reply logic:
The bot uses Claude AI, so it needs `ANTHROPIC_API_KEY` set. Without it, the bot runs in DEMO MODE.

## Next Steps

1. **Deploy to Railway** (if not already deployed)
   ```bash
   cd /Users/jimmy/CannaPeace/products/nova/demos/restaurant-line-to-excel
   railway up
   ```

2. **Update LINE webhook URL** in LINE Developers Console:
   ```
   https://your-railway-domain.up.railway.app/webhook
   ```

3. **Test with real LINE messages** from your phone!

4. **Add more strains** (if needed):
   - Add new PNG image to `product_images/v6/`
   - Update `customer_config.json` with strain details
   - Bot will automatically serve the new image

## File Size Considerations

The images are 7-8 MB each, which is fine for LINE. LINE supports images up to 10 MB.

If you need to optimize:
```bash
# Optional: Compress images while maintaining quality
cd product_images/v6/
for f in *.png; do
    convert "$f" -quality 85 -define png:compression-level=9 "optimized_$f"
done
```

## Support

The integration is complete and ready to use! The bot will now automatically send strain images when customers ask about specific strains.

All 7 strain images are loaded and ready to go! 🌿
