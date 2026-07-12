#!/usr/bin/env python3
"""
Restaurant LINE-to-Excel Order Bridge (D2)
===========================================
2-Day Demo | Happy Path Only | Sample Data

Receives LINE messages with restaurant orders (Thai/Chinese/English mixed),
parses them using GPT-4, appends to Google Sheet.

DEMO MODE: Works with sample data without real LINE webhook or API keys.
"""

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import anthropic
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel

app = FastAPI(title="Restaurant LINE-to-Excel Bridge")

# Configuration (with fallbacks for demo mode)
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "DEMO_MODE")
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "DEMO_MODE")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
GOOGLE_CREDENTIALS_BASE64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "DEMO_SHEET")

# Load sample orders
SAMPLE_ORDERS = json.loads(Path("sample_orders.json").read_text()) if Path("sample_orders.json").exists() else {"sample_orders": []}

# Initialize services (with demo fallbacks)
def get_anthropic_client():
    if ANTHROPIC_API_KEY:
        return anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return None

def get_sheets_service():
    # Try base64-encoded credentials first (for Railway deployment)
    if GOOGLE_CREDENTIALS_BASE64:
        import base64
        creds_json = base64.b64decode(GOOGLE_CREDENTIALS_BASE64).decode('utf-8')
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=credentials)

    # Fall back to file path
    if Path(GOOGLE_CREDENTIALS_PATH).exists():
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=credentials)
    return None

anthropic_client = get_anthropic_client()
sheets_service = get_sheets_service()

if LINE_CHANNEL_SECRET != "DEMO_MODE":
    line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
    handler = WebhookHandler(LINE_CHANNEL_SECRET)
else:
    line_bot_api = None
    handler = None

# Models
class OrderItem(BaseModel):
    name: str
    quantity: int
    price: Optional[float] = None

class ParsedOrder(BaseModel):
    customer_name: str
    phone: str
    items: List[OrderItem]
    total: float
    notes: Optional[str] = None
    timestamp: str = None

# Order Parser
async def parse_order_message(message: str) -> ParsedOrder:
    """Parse order message using Claude or sample data"""

    if not anthropic_client:
        # DEMO MODE: Return sample parsed order
        return ParsedOrder(
            customer_name="Demo Customer",
            phone="081-234-5678",
            items=[
                OrderItem(name="ผัดไทย", quantity=2, price=200),
                OrderItem(name="ต้มยำกุ้ง", quantity=1, price=150)
            ],
            total=350,
            timestamp=datetime.now().isoformat()
        )

    prompt = f"""Parse this restaurant order message into structured JSON.
The message may be in Thai, Chinese, or English (or mixed).

Order message:
{message}

Extract:
- customer_name: Customer name
- phone: Phone number (format: XXX-XXX-XXXX or similar)
- items: List of {{name, quantity, price}} (price optional)
- total: Total amount in THB
- notes: Any special instructions (optional)

Return JSON only, no markdown:
{{
  "customer_name": "...",
  "phone": "...",
  "items": [
    {{"name": "...", "quantity": 2, "price": 100}}
  ],
  "total": 350,
  "notes": "..."
}}
"""

    response = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = response.content[0].text

    # Claude may wrap JSON in markdown code blocks, strip them
    if response_text.startswith("```json"):
        response_text = response_text[7:]  # Remove ```json
    if response_text.startswith("```"):
        response_text = response_text[3:]  # Remove ```
    if response_text.endswith("```"):
        response_text = response_text[:-3]  # Remove trailing ```

    parsed = json.loads(response_text.strip())
    parsed["timestamp"] = datetime.now().isoformat()

    return ParsedOrder(**parsed)

# Google Sheets Integration
async def append_to_sheet(order: ParsedOrder) -> bool:
    """Append parsed order to Google Sheet"""

    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        # DEMO MODE: Just log
        print(f"[DEMO] Would append to sheet: {order.model_dump()}")
        return True

    # Prepare row data
    items_str = ", ".join([f"{item.name} x{item.quantity}" for item in order.items])

    row = [
        order.timestamp,
        order.customer_name,
        order.phone,
        items_str,
        order.total,
        order.notes or ""
    ]

    body = {
        'values': [row]
    }

    try:
        sheets_service.spreadsheets().values().append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Orders!A:F',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"Error appending to sheet: {e}")
        return False

# Routes
@app.get("/", response_class=HTMLResponse)
async def index():
    """Demo UI for testing order parsing"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Restaurant LINE-to-Excel Bridge - DEMO MODE</title>
        <meta charset="UTF-8">
        <style>
            body { font-family: 'Segoe UI', Arial, sans-serif; max-width: 1000px; margin: 50px auto; padding: 20px; }
            h1 { color: #06c755; }
            .section { background: #f5f5f5; padding: 20px; margin: 20px 0; border-radius: 8px; }
            textarea { width: 100%; min-height: 150px; padding: 10px; border: 1px solid #ccc; border-radius: 4px; font-family: monospace; }
            button { background: #06c755; color: white; padding: 12px 24px; border: none; border-radius: 4px; cursor: pointer; font-size: 16px; }
            button:hover { background: #05b04b; }
            .result { margin-top: 20px; white-space: pre-wrap; font-family: monospace; }
            .sample { background: white; padding: 10px; margin: 10px 0; border-left: 3px solid #06c755; cursor: pointer; }
            .sample:hover { background: #f9f9f9; }
        </style>
    </head>
    <body>
        <h1>🍜 Restaurant LINE-to-Excel Bridge</h1>
        <div style="background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; border-radius: 4px;">
            <strong>⚠️ DEMO MODE:</strong> Using sample data. Connect LINE bot + Google Sheets for live operation.
        </div>
        <p><strong>Parse Thai/Chinese/English restaurant orders automatically</strong></p>

        <div class="section">
            <h2>Sample Orders (Click to Test)</h2>
            <div id="samples"></div>
        </div>

        <div class="section">
            <h2>Or Enter Custom Order Message</h2>
            <textarea id="orderText" placeholder="Paste order message here...&#10;&#10;Example:&#10;สั่งอาหาร:&#10;- ผัดไทย 2 จาน&#10;- ต้มยำกุ้ง 1 ถ้วย&#10;รวม 350 บาท&#10;ชื่อ: คุณสมชาย&#10;โทร: 081-234-5678"></textarea>
            <button onclick="parseOrder()">Parse Order</button>
            <div class="result" id="result"></div>
        </div>

        <script>
            // Load samples
            fetch('/samples')
                .then(r => r.json())
                .then(data => {
                    const samplesDiv = document.getElementById('samples');
                    data.sample_orders.forEach(order => {
                        const div = document.createElement('div');
                        div.className = 'sample';
                        div.innerHTML = `<strong>Order ${order.id}:</strong><br>${order.message.substring(0, 100)}...`;
                        div.onclick = () => {
                            document.getElementById('orderText').value = order.message;
                        };
                        samplesDiv.appendChild(div);
                    });
                });

            async function parseOrder() {
                const text = document.getElementById('orderText').value;
                if (!text) {
                    alert('Please enter an order message');
                    return;
                }

                document.getElementById('result').textContent = 'Parsing...';

                try {
                    const response = await fetch('/parse', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({message: text})
                    });

                    const data = await response.json();
                    document.getElementById('result').textContent = JSON.stringify(data, null, 2);
                } catch (error) {
                    document.getElementById('result').textContent = 'Error: ' + error.message;
                }
            }
        </script>
    </body>
    </html>
    """

@app.get("/samples")
async def get_samples():
    """Return sample orders"""
    return SAMPLE_ORDERS

@app.post("/parse")
async def parse_order(request: Request):
    """Parse order message (for testing)"""
    body = await request.json()
    message = body.get("message", "")

    if not message:
        raise HTTPException(status_code=400, detail="No message provided")

    parsed = await parse_order_message(message)
    appended = await append_to_sheet(parsed)

    return {
        "parsed_order": parsed.model_dump(),
        "appended_to_sheet": appended,
        "mode": "DEMO" if not anthropic_client else "LIVE"
    }

@app.post("/webhook")
async def webhook(request: Request):
    """LINE webhook endpoint"""

    if not handler:
        return JSONResponse({"status": "DEMO_MODE", "message": "LINE webhook not configured"})

    signature = request.headers.get('X-Line-Signature', '')
    body = await request.body()

    try:
        handler.handle(body.decode(), signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="Invalid signature")

    return JSONResponse({"status": "ok"})

def handle_message(event):
    """Handle incoming LINE messages (note: LINE bot SDK doesn't support async handlers)"""
    try:
        import asyncio
        message_text = event.message.text

        # Parse order using Claude AI
        parsed_order = asyncio.run(parse_order_message(message_text))

        # Load customer config for templates
        config = json.loads(Path("customer_config.json").read_text())
        template = config["templates"]["order_received_thai"]

        # Format items for display
        items_str = ", ".join([f"{item.name} x{item.quantity}" for item in parsed_order.items])

        # Format reply using template
        reply = template.format(
            items=items_str,
            total=f"{parsed_order.total:,.0f}",
            currency=config.get("currency_symbol", "฿")
        )

        # Append to Google Sheets (async call needs to run in event loop)
        asyncio.run(append_to_sheet(parsed_order))

        if line_bot_api:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text=reply)
            )
    except Exception as e:
        print(f"Error handling message: {e}")
        # Send error message to user
        if line_bot_api:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล")
            )

# Register handler only if LINE is configured
if handler:
    handler.add(MessageEvent, message=TextMessage)(handle_message)

@app.get("/daily-summary")
async def get_daily_summary():
    """Generate daily summary of orders"""

    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        # DEMO MODE: Return sample summary
        return {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "total_orders": 10,
            "total_revenue": 4850,
            "top_items": [
                {"name": "ผัดไทย", "quantity": 12},
                {"name": "ต้มยำกุ้ง", "quantity": 8},
                {"name": "ข้าวผัด", "quantity": 7}
            ],
            "summary_message": "📊 สรุปยอดวันนี้ (Demo)\n\n📦 ออเดอร์: 10 รายการ\n💰 ยอดรวม: 4,850 บาท\n\n🔥 เมนูขายดี:\n1. ผัดไทย (12 จาน)\n2. ต้มยำกุ้ง (8 ถ้วย)\n3. ข้าวผัด (7 จาน)",
            "mode": "DEMO"
        }

    # Fetch today's orders from sheet
    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Orders!A:F'
        ).execute()

        rows = result.get('values', [])
        today = datetime.now().strftime("%Y-%m-%d")

        # Filter today's orders
        today_orders = [row for row in rows if row and row[0].startswith(today)]

        total_orders = len(today_orders)
        total_revenue = sum(float(row[4]) for row in today_orders if len(row) > 4)

        # Count items
        item_counts = {}
        for row in today_orders:
            if len(row) > 3:
                items = row[3].split(", ")
                for item_str in items:
                    # Parse "ผัดไทย x2"
                    parts = item_str.split(" x")
                    item_name = parts[0]
                    qty = int(parts[1]) if len(parts) > 1 else 1
                    item_counts[item_name] = item_counts.get(item_name, 0) + qty

        # Top 3 items
        top_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        top_items_list = [{"name": name, "quantity": qty} for name, qty in top_items]

        # Build summary message (Thai)
        summary_msg = f"📊 สรุปยอดวันนี้\n\n"
        summary_msg += f"📦 ออเดอร์: {total_orders} รายการ\n"
        summary_msg += f"💰 ยอดรวม: {total_revenue:,.0f} บาท\n\n"

        if top_items_list:
            summary_msg += "🔥 เมนูขายดี:\n"
            for i, item in enumerate(top_items_list, 1):
                summary_msg += f"{i}. {item['name']} ({item['quantity']} รายการ)\n"

        return {
            "date": today,
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "top_items": top_items_list,
            "summary_message": summary_msg,
            "mode": "LIVE"
        }

    except Exception as e:
        print(f"Error fetching daily summary: {e}")
        return {"error": str(e)}

@app.get("/health")
async def health():
    """Health check"""
    import os
    cwd = os.getcwd()
    config_exists = Path("customer_config.json").exists()
    sample_exists = Path("sample_orders.json").exists()

    return {
        "status": "ok",
        "mode": "DEMO" if not anthropic_client else "LIVE",
        "line_webhook": "configured" if handler else "demo",
        "google_sheets": "configured" if sheets_service else "demo",
        "cwd": cwd,
        "customer_config_exists": config_exists,
        "sample_orders_exists": sample_exists
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Restaurant LINE-to-Excel Bridge (Demo)")
    print(f"📍 Open: http://localhost:8001")
    print(f"🔧 Mode: {'DEMO' if not anthropic_client else 'LIVE'}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
