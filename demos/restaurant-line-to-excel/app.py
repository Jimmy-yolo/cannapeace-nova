#!/usr/bin/env python3
"""
Restaurant LINE-to-Excel Order Bridge (D2)
===========================================
2-Day Demo | Happy Path Only | Sample Data

Receives LINE messages with restaurant orders (Thai/Chinese/English mixed),
parses them using GPT-4, appends to Google Sheet.

DEMO MODE: Works with sample data without real LINE webhook or API keys.
"""

from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage
import anthropic
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
from pathlib import Path
import json
import os
from typing import Dict, List, Optional
from pydantic import BaseModel
from urllib.parse import quote

app = FastAPI(title="Restaurant LINE-to-Excel Bridge")

# Mount static files for strain images
PRODUCT_IMAGES_PATH = Path(__file__).parent / "product_images" / "v6"
if PRODUCT_IMAGES_PATH.exists():
    app.mount("/strain-images", StaticFiles(directory=str(PRODUCT_IMAGES_PATH)), name="strain-images")

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

# Conversation Memory (user_id -> conversation history)
conversation_memory = {}
MAX_CONVERSATION_HISTORY = 10  # Keep last 10 messages per user

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
def parse_order_message_sync(message: str) -> ParsedOrder:
    """Parse order message using Claude or sample data (synchronous)"""

    if not anthropic_client:
        # DEMO MODE: Return sample parsed order
        return ParsedOrder(
            customer_name="Demo Customer",
            phone="081-234-5678",
            items=[
                OrderItem(name="Thai Stick", quantity=5, price=400),
                OrderItem(name="Mango Kush", quantity=3, price=350)
            ],
            total=2450,
            timestamp=datetime.now().isoformat()
        )

    prompt = f"""Parse this cannabis order message into structured JSON.
The message may be in Thai or English (or mixed).

Order message:
{message}

Extract:
- customer_name: Customer name (if not provided, use "Customer")
- phone: Phone number (if not provided, use "Not provided")
- items: List of {{name, quantity, price_per_gram}}
  - quantity should be in grams
  - price_per_gram: use these prices:
    - Thai Stick: 400 THB/g
    - Mango Kush: 350 THB/g
    - Northern Lights: 450 THB/g
    - Super Lemon Haze: 420 THB/g
    - Blueberry Kush: 380 THB/g
    - Pineapple Express: 400 THB/g
- total: Total amount in THB (sum of quantity * price_per_gram for all items)
- notes: Any special instructions (optional)

Return JSON only, no markdown:
{{
  "customer_name": "...",
  "phone": "...",
  "items": [
    {{"name": "Thai Stick", "quantity": 5, "price": 2000}}
  ],
  "total": 2000,
  "notes": ""
}}
"""

    response = anthropic_client.messages.create(
        model="claude-sonnet-4-6",
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
def append_to_sheet_sync(order: ParsedOrder) -> bool:
    """Append parsed order to Google Sheet (synchronous)"""

    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        # DEMO MODE: Just log
        print(f"[DEMO] Would append to sheet: {order.model_dump()}")
        return True

    # Prepare row data
    items_str = ", ".join([f"{item.name} x{item.quantity}g" for item in order.items])

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
            range='Sheet1!A:F',  # Use default sheet name
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        return True
    except Exception as e:
        print(f"Error appending to sheet: {e}")
        import traceback
        traceback.print_exc()
        raise  # Re-raise so /parse endpoint shows the error

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

    parsed = parse_order_message_sync(message)
    appended = append_to_sheet_sync(parsed)

    return {
        "parsed_order": parsed.model_dump(),
        "appended_to_sheet": appended,
        "mode": "DEMO" if not anthropic_client else "LIVE"
    }

@app.post("/webhook")
async def webhook(request: Request, background_tasks: BackgroundTasks):
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
    """Handle incoming LINE messages - Conversational AI version"""
    try:
        message_text = event.message.text
        user_id = event.source.user_id if hasattr(event.source, 'user_id') else "demo_user"

        # Check if Claude is configured
        if not anthropic_client:
            if line_bot_api:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ DEMO MODE - Claude AI not configured")
                )
            return

        # Load conversation history
        if user_id not in conversation_memory:
            conversation_memory[user_id] = []

        conversation_history = conversation_memory[user_id]

        # Build conversation context
        history_text = ""
        if conversation_history:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-MAX_CONVERSATION_HISTORY:]])

        # Load product catalog
        config = json.loads(Path("customer_config.json").read_text())
        products_info = "\n".join([
            f"- {p['name_english']} ({p['name_thai']}): {p['price_per_gram']}฿/g - {p['strain_type']} {p['thc']} THC"
            for p in config["products"]
        ])

        # Conversational AI prompt
        prompt = f"""You are a friendly customer service agent for CannaPeace (แคนนาพีซ), a premium cannabis shop in Thailand.

CONVERSATION HISTORY:
{history_text if history_text else "(New conversation)"}

CUSTOMER'S NEW MESSAGE:
{message_text}

YOUR PRODUCTS:
{products_info}

YOUR ROLE:
1. If greeting (hi/hello/สวัสดี) → Greet warmly in Thai/English
2. If asking about menu/products (what do you have/menu/รายการ) → Show the menu with short descriptions
3. If asking about SPECIFIC strain → Say "SEND_IMAGE:strain_name" then describe it in detail
4. If placing an order:
   - Extract items and quantities
   - Ask for PHONE NUMBER if not provided
   - Ask for DELIVERY ADDRESS if not provided
   - When ALL info complete, confirm order

MENU FORMAT (when showing menu):
🌿 **CannaPeace Menu** 🌿
All strains: 450฿ per 10g

1. Capjunky (Hybrid 28% THC) - Sweet, relaxing
2. Alien Marker (Indica 26% THC) - Deep relaxation
3. Trop Cherry (Hybrid 27% THC) - Tropical, fruity
4. Gogurtz (Hybrid 29% THC) - Creamy, dessert
5. Berry Bonds (Indica 25% THC) - Berry, evening
6. LCG x Grapegas (Hybrid 30% THC) - Gassy, strong
7. Apple Banana (Sativa 24% THC) - Uplifting, fruity

💬 Ask about any strain for details!

IMPORTANT:
- When user asks about SPECIFIC strain, respond with:
  SEND_IMAGE:strain_english_name
  Then describe the strain

- When order is COMPLETE (has phone + address):
  ORDER_COMPLETE:{{"customer_name": "...", "phone": "...", "address": "...", "items": [{{"name": "...", "quantity": X, "price": Y}}], "total": Z}}

Respond now:"""

        # Call Claude
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )

        bot_reply = response.content[0].text.strip()

        # Update conversation history
        conversation_memory[user_id].append({"role": "user", "content": message_text})
        conversation_memory[user_id].append({"role": "assistant", "content": bot_reply})

        # Check if order is complete
        if "ORDER_COMPLETE:" in bot_reply:
            try:
                # Extract JSON from response
                json_start = bot_reply.index("ORDER_COMPLETE:") + len("ORDER_COMPLETE:")
                json_str = bot_reply[json_start:].strip()

                # Find JSON object
                if json_str.startswith("{"):
                    json_end = json_str.index("}") + 1
                    json_str = json_str[:json_end]

                order_data = json.loads(json_str)

                # Remove ORDER_COMPLETE from reply
                bot_reply = bot_reply[:bot_reply.index("ORDER_COMPLETE:")].strip()

                # Save to Google Sheets
                if sheets_service and GOOGLE_SHEET_ID != "DEMO_SHEET":
                    items_str = ", ".join([f"{item['name']} x{item['quantity']}g" for item in order_data["items"]])
                    row = [
                        datetime.now().isoformat(),
                        order_data.get("customer_name", "Customer"),
                        order_data.get("phone", "Not provided"),
                        items_str,
                        order_data["total"],
                        order_data.get("address", "") + " " + order_data.get("notes", "")
                    ]

                    body = {'values': [row]}
                    sheets_service.spreadsheets().values().append(
                        spreadsheetId=GOOGLE_SHEET_ID,
                        range='Sheet1!A:F',
                        valueInputOption='USER_ENTERED',
                        insertDataOption='INSERT_ROWS',
                        body=body
                    ).execute()

                    print(f"✅ Order saved to sheet for user {user_id}")

                # Clear conversation after successful order
                conversation_memory[user_id] = []

            except Exception as sheet_error:
                print(f"Sheet error: {sheet_error}")

        # Check if bot wants to send product image
        image_to_send = None
        if "SEND_IMAGE:" in bot_reply:
            try:
                # Extract strain name
                image_marker = "SEND_IMAGE:"
                start_idx = bot_reply.index(image_marker) + len(image_marker)
                end_idx = bot_reply.index("\n", start_idx) if "\n" in bot_reply[start_idx:] else len(bot_reply)
                strain_name = bot_reply[start_idx:end_idx].strip()

                # Find product image URL using real strain images from product_images/v6/
                # Image filenames match display names (e.g., "Alien Marker.png")

                # Name mappings for variations
                name_mappings = {
                    "trop cherry": "Tropical Cherry",
                    "tropical cherry": "Tropical Cherry",
                    "lcg x grapegas": "Grape Gas",  # If you have Grape Gas image
                    "any day": "Any Day",
                    "miracle mints": "Miracle Mints"
                }

                # Try direct match first
                image_filename = f"{strain_name}.png"
                image_path = PRODUCT_IMAGES_PATH / image_filename

                # If not found, try mapped name
                if not image_path.exists() and strain_name.lower() in name_mappings:
                    mapped_name = name_mappings[strain_name.lower()]
                    image_filename = f"{mapped_name}.png"
                    image_path = PRODUCT_IMAGES_PATH / image_filename

                if image_path.exists():
                    # Use Railway URL or localhost for image serving
                    base_url = os.getenv("PUBLIC_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000"))
                    if not base_url.startswith("http"):
                        base_url = f"https://{base_url}"

                    # URL-encode the filename to handle spaces (e.g., "Cap Junky.png" -> "Cap%20Junky.png")
                    encoded_filename = quote(image_filename)
                    image_url = f"{base_url}/strain-images/{encoded_filename}"
                    image_to_send = image_url
                    print(f"📸 Sending image for: {strain_name} from {image_url}")
                else:
                    print(f"⚠️ Image not found for: {strain_name} (tried: {image_filename})")
                    # List available images for debugging
                    if PRODUCT_IMAGES_PATH.exists():
                        available = [f.name for f in PRODUCT_IMAGES_PATH.glob("*.png")]
                        print(f"Available images: {', '.join(available)}")

                # Remove SEND_IMAGE marker from text
                bot_reply = bot_reply[:bot_reply.index(image_marker)] + bot_reply[end_idx+1:]
                bot_reply = bot_reply.strip()

            except Exception as img_error:
                print(f"Image error: {img_error}")
                import traceback
                traceback.print_exc()

        # Send reply (image + text if applicable)
        if line_bot_api:
            messages = []

            # Add image if requested
            if image_to_send:
                messages.append(ImageSendMessage(
                    original_content_url=image_to_send,
                    preview_image_url=image_to_send
                ))

            # Add text reply
            messages.append(TextSendMessage(text=bot_reply))

            line_bot_api.reply_message(event.reply_token, messages)

    except Exception as e:
        print(f"Error handling message: {e}")
        import traceback
        traceback.print_exc()
        if line_bot_api:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="❌ ขออภัยค่ะ เกิดข้อผิดพลาดในการประมวลผล กรุณาลองใหม่อีกครั้งค่ะ")
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

    # Debug: Check product images path
    images_path_exists = PRODUCT_IMAGES_PATH.exists()
    images_path_str = str(PRODUCT_IMAGES_PATH)
    images_count = len(list(PRODUCT_IMAGES_PATH.glob("*.png"))) if images_path_exists else 0

    return {
        "status": "ok",
        "mode": "DEMO" if not anthropic_client else "LIVE",
        "line_webhook": "configured" if handler else "demo",
        "google_sheets": "configured" if sheets_service else "demo",
        "cwd": cwd,
        "customer_config_exists": config_exists,
        "sample_orders_exists": sample_exists,
        "product_images_path": images_path_str,
        "product_images_exists": images_path_exists,
        "product_images_count": images_count
    }

@app.get("/strain-images-list")
async def list_strain_images():
    """List all available strain images"""
    if not PRODUCT_IMAGES_PATH.exists():
        return {"error": "Product images directory not found"}

    images = []
    for img_file in PRODUCT_IMAGES_PATH.glob("*.png"):
        base_url = os.getenv("PUBLIC_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000"))
        if not base_url.startswith("http"):
            base_url = f"https://{base_url}"

        # URL-encode filename to handle spaces
        encoded_filename = quote(img_file.name)

        images.append({
            "filename": img_file.name,
            "strain_name": img_file.stem,  # Name without extension
            "url": f"{base_url}/strain-images/{encoded_filename}",
            "size_mb": round(img_file.stat().st_size / (1024 * 1024), 2)
        })

    return {
        "total_images": len(images),
        "images": sorted(images, key=lambda x: x["strain_name"]),
        "base_url": os.getenv("PUBLIC_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000"))
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Restaurant LINE-to-Excel Bridge (Demo)")
    print(f"📍 Open: http://localhost:8001")
    print(f"🔧 Mode: {'DEMO' if not anthropic_client else 'LIVE'}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
