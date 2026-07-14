# CannaPeace AI Platform

**v1.0 → v2.0** | Omnichannel Customer Engagement System for Cannabis Retail

## What It Is

AI-powered customer service platform for CannaPeace, currently live on LINE with planned expansion to Facebook Messenger, Instagram DM, TikTok Chat, and social media auto-reply.

**Production URL:** https://cannapeace-nova-production.up.railway.app

## Current Features (v1.0)

- **LINE Bot Integration** - Conversational AI customer service on LINE
- **Claude AI (Sonnet 4)** - Natural language understanding and response generation
- **Strain Recommendations** - 7 premium strains with product images
  - Cap Junky (Miracle Mints), Alien Marker, Trop Cherry, Gogurtz, Berry Bonds, LCG x Grapegas (Any Day), Apple Banana
- **Visual Product Catalog** - Automated strain image delivery via HTTPS
- **Order Processing** - Automatic order capture to Google Sheets
- **Typing Indicators** - Natural conversation feel
- **Multi-language Support** - Thai, Chinese, English
- **Performance Monitoring** - Response time tracking (2-4s average)

## Tech Stack

- **FastAPI** - High-performance webhook server
- **LINE Messaging API** - Chat platform integration
- **Claude AI (Anthropic)** - Conversational intelligence
- **Google Sheets API** - Order database
- **Railway** - Production deployment platform
- **Python 3.11+** - Runtime environment

## Coming Soon (v2.0 - CRM Implementation)

**Timeline:** Week 1-4 (July 2026)

- **Customer Profiles** - Track every customer across channels
- **Journey Tracking** - 7-stage customer funnel analytics
- **Lifetime Value** - Auto-calculated per customer
- **Customer Segmentation** - VIP, repeat, new, at-risk, inactive
- **Persistent Chat History** - Conversations survive restarts
- **Multi-Channel Attribution** - Know which platform drives sales

See `MIGRATION_TO_ADVANCED_CRM.md` for implementation plan.

## Future Expansion (Multi-Channel)

**Timeline:** Month 2+ (August 2026+)

- **Facebook Messenger** - Same AI, new platform
- **Instagram DM** - Unified customer experience
- **TikTok Chat** - Engage customers where they discover you
- **Social Media Auto-Reply** - AI-powered comment engagement
  - Auto-answer questions on posts
  - Auto-like positive comments
  - Alert operator for issues
  - Filter spam intelligently

See `OMNICHANNEL_EXPANSION_ROADMAP.md` for complete vision.

## Quick Start

### Prerequisites

- Python 3.11+
- LINE Official Account
- Anthropic API key (Claude)
- Google Cloud project with Sheets API enabled
- Railway account (for deployment)

### Local Development

```bash
# Clone and navigate
cd /Users/jimmy/CannaPeace/products/nova/demos/cannapeace-ai-platform

# Install dependencies
pip install -r requirements.txt

# Configure environment (see .env.example)
cp .env.example .env
# Edit .env with your credentials

# Run locally
python app.py

# Test with ngrok
ngrok http 8000
# Update LINE webhook URL to ngrok URL + /webhook
```

See `LOCAL_DEV_GUIDE.md` for detailed setup instructions.

### Production Deployment

```bash
# Deploy to Railway (auto-deploys from git)
railway up

# Or use the deployment script
./deploy-to-railway.sh
```

See `RAILWAY_SETUP.md` for deployment guide.

## Project Structure

```
.
├── app.py                          # Main application (744 lines)
├── customer_config.json            # Strain catalog (7 products)
├── product_images/v6/              # Strain images (7 PNG files, ~53MB)
├── requirements.txt                # Python dependencies
├── railway.json                    # Railway deployment config
├── .env.example                    # Environment variables template
│
├── MIGRATION_TO_ADVANCED_CRM.md    # v2.0 CRM implementation plan
├── OMNICHANNEL_EXPANSION_ROADMAP.md # Multi-channel strategy
├── SESSION_HANDOFF_CRM_PRIORITY.md # Next session starting point
│
└── docs/                           # Additional documentation
```

## Environment Variables

Required in Railway or `.env`:

- `LINE_CHANNEL_SECRET` - LINE Developer Console
- `LINE_CHANNEL_ACCESS_TOKEN` - LINE Developer Console
- `ANTHROPIC_API_KEY` - Anthropic Console
- `GOOGLE_CREDENTIALS_BASE64` - Base64-encoded service account JSON
- `GOOGLE_SHEET_ID` - Target Google Sheet ID
- `PUBLIC_URL` - Production URL (Railway auto-sets)

See `CONFIG_INSTRUCTIONS.md` for detailed configuration.

## Documentation

### Essential Guides
- `SESSION_HANDOFF_CRM_PRIORITY.md` - **START HERE for v2.0 CRM implementation**
- `MIGRATION_TO_ADVANCED_CRM.md` - How to build v2.0 on v1.0
- `OMNICHANNEL_EXPANSION_ROADMAP.md` - Multi-channel expansion plan
- `CRM_IMPLEMENTATION_PLAN.md` - 4 levels of CRM architecture

### Setup & Deployment
- `LOCAL_DEV_GUIDE.md` - Local development setup
- `RAILWAY_SETUP.md` - Railway deployment
- `CONFIG_INSTRUCTIONS.md` - Environment configuration
- `LINE_OA_SETUP_GUIDE.md` - LINE Official Account setup

### Technical Details
- `PERFORMANCE_ANALYSIS.md` - Response time breakdown
- `STRAIN_IMAGE_AUTO_REPLY_SETUP.md` - Image integration
- `smoke_test.md` - Testing procedures

### Advanced CRM Design
Located in `/Users/jimmy/CannaPeace/outputs/`:
- `LINE_CRM_MARKETING_SYSTEM_DESIGN.md` - Complete system architecture (75 pages)
- `CODE_EXAMPLES_LINE_BOT.md` - Full working code examples
- `IMPLEMENTATION_CHECKLIST.md` - 100+ tasks across 5 phases
- `COST_ANALYSIS_AND_ROI.md` - Financial projections
- `QUICK_REFERENCE_GUIDE.md` - Quick lookup

## Development History

- **v1.0.0** - Initial LINE bot with Claude AI
- **v1.0.1** - Added strain images and typing indicators
- **v1.0** - Renamed to CannaPeace AI Platform (July 2026)
- **v2.0** - CRM implementation (in progress)

Previous name: `restaurant-line-to-excel` (renamed July 14, 2026)

## Cost Estimate

**v1.0 (Current):**
- Railway hosting: ฿360/month
- Claude AI (500 conversations): ฿20-40/month
- **Total: ~฿380-400/month**

**v2.0 (CRM):**
- Same cost (uses existing Google Sheets)

**Multi-Channel (Future):**
- Railway hosting: ฿360/month
- Claude AI (3000 conversations): ฿60-150/month
- All platform APIs: Free
- **Total: ~฿420-510/month** for 5+ platforms

## License

Proprietary - CannaPeace NOVA Project

## Support

For issues or questions, see session handoff documents or contact development team.

---

**Last Updated:** 2026-07-14
**Status:** v1.0 Production, v2.0 CRM In Progress
