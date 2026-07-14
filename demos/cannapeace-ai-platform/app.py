#!/usr/bin/env python3
"""
CannaPeace AI Platform - Omnichannel Customer Engagement System
================================================================
v1.0 → v2.0 (CRM + Multi-Channel Expansion)

AI-powered customer service platform for cannabis retail.
Currently supports LINE with planned expansion to:
- Facebook Messenger
- Instagram DM
- TikTok Chat
- Social media auto-reply (comments)

Features:
- Claude AI conversational service (Thai/English)
- Customer journey tracking & CRM
- Multi-channel attribution
- Automated strain recommendations
- Google Sheets + future PostgreSQL backend

v1.0: LINE bot with strain images, orders, conversation memory
v2.0: CRM, attribution, customer profiles, multi-channel foundation
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

app = FastAPI(title="CannaPeace AI Platform - Omnichannel Customer Engagement")

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

# Load customer config
CUSTOMER_CONFIG = json.loads(Path("customer_config.json").read_text()) if Path("customer_config.json").exists() else {"supported_languages": {}}

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

# CRM: Customer journey stages
JOURNEY_STAGES = [
    "Initial Contact",
    "Menu Inquiry",
    "Product Question",
    "Address Collection",
    "Order Intent",
    "Order Placement",
    "Completion"
]

# CRM: Auto-setup Google Sheets structure
def ensure_crm_sheets_exist():
    """Ensure all CRM sheets exist with proper headers (idempotent)"""
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return

    try:
        # Get existing sheets
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=GOOGLE_SHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', [])
        sheet_titles = {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheets}

        # Define sheet structures
        crm_sheets = {
            'Orders': [
                'Timestamp', 'LINE_User_ID', 'Name', 'Phone', 'Items',
                'Total', 'Address', 'Status', 'Attribution_Source'
            ],
            'Customers': [
                'LINE_User_ID', 'Phone', 'Name', 'First_Seen', 'Last_Seen',
                'Language_Preference', 'Total_Orders', 'Lifetime_Value', 'Acquisition_Source',
                'Current_Journey_Stage', 'Segment', 'Favorite_Strains', 'Tags'
            ],
            'Messages': [
                'Timestamp', 'LINE_User_ID', 'Direction', 'Content',
                'Detected_Intent', 'Journey_Stage_Before', 'Journey_Stage_After'
            ],
            'Journey_Events': [
                'Event_ID', 'LINE_User_ID', 'Event_Type', 'From_Stage',
                'To_Stage', 'Timestamp', 'Metadata'
            ],
            'Attribution_Links': [
                'Link_ID', 'Channel', 'UTM_Campaign', 'UTM_Medium',
                'UTM_Source', 'Total_Clicks', 'Total_Conversions', 'Revenue', 'Created_Date'
            ]
        }

        # Rename Sheet1 to Orders if needed
        if 'Sheet1' in sheet_titles and 'Orders' not in sheet_titles:
            request = {
                'requests': [{
                    'updateSheetProperties': {
                        'properties': {
                            'sheetId': sheet_titles['Sheet1'],
                            'title': 'Orders'
                        },
                        'fields': 'title'
                    }
                }]
            }
            sheets_service.spreadsheets().batchUpdate(
                spreadsheetId=GOOGLE_SHEET_ID, body=request
            ).execute()
            print("✅ Renamed Sheet1 to Orders")
            sheet_titles['Orders'] = sheet_titles.pop('Sheet1')

        # Create missing sheets
        for sheet_name, headers in crm_sheets.items():
            if sheet_name not in sheet_titles:
                request = {
                    'requests': [{
                        'addSheet': {
                            'properties': {'title': sheet_name}
                        }
                    }]
                }
                sheets_service.spreadsheets().batchUpdate(
                    spreadsheetId=GOOGLE_SHEET_ID, body=request
                ).execute()
                print(f"✅ Created sheet '{sheet_name}'")

                # Add headers
                body = {'values': [headers]}
                sheets_service.spreadsheets().values().update(
                    spreadsheetId=GOOGLE_SHEET_ID,
                    range=f'{sheet_name}!A1',
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                print(f"✅ Added headers to '{sheet_name}'")

        # Update Customers sheet headers if they exist (fix column order)
        if 'Customers' in sheet_titles:
            try:
                result = sheets_service.spreadsheets().values().get(
                    spreadsheetId=GOOGLE_SHEET_ID,
                    range='Customers!A1:M1'
                ).execute()
                existing_headers = result.get('values', [[]])[0] if result.get('values') else []
                correct_headers = crm_sheets['Customers']

                # Update headers if they don't match
                if existing_headers != correct_headers:
                    body = {'values': [correct_headers]}
                    sheets_service.spreadsheets().values().update(
                        spreadsheetId=GOOGLE_SHEET_ID,
                        range='Customers!A1:M1',
                        valueInputOption='USER_ENTERED',
                        body=body
                    ).execute()
                    print(f"✅ Updated Customers sheet headers (fixed column order)")
            except Exception as e:
                print(f"⚠️ Could not update Customers headers: {e}")

        print("✅ CRM sheets structure verified/created")

    except Exception as e:
        print(f"⚠️ Error setting up CRM sheets: {e}")
        # Don't fail the app startup, just log the error

# CRM: Customer Profile Management
def get_customer_profile(user_id: str) -> Optional[dict]:
    """Get customer profile from Customers sheet"""
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return None

    try:
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Customers!A:M'
        ).execute()

        rows = result.get('values', [])
        if len(rows) <= 1:  # Only headers or empty
            return None

        # Find customer by LINE_User_ID (column A)
        for row in rows[1:]:  # Skip header
            if row and row[0] == user_id:
                return {
                    'line_user_id': row[0] if len(row) > 0 else '',
                    'phone': row[1] if len(row) > 1 else '',
                    'name': row[2] if len(row) > 2 else '',
                    'first_seen': row[3] if len(row) > 3 else '',
                    'last_seen': row[4] if len(row) > 4 else '',
                    'language_preference': row[5] if len(row) > 5 else 'thai',
                    'total_orders': int(row[6]) if len(row) > 6 and row[6] else 0,
                    'lifetime_value': float(row[7]) if len(row) > 7 and row[7] else 0.0,
                    'acquisition_source': row[8] if len(row) > 8 else 'LINE',
                    'current_journey_stage': row[9] if len(row) > 9 else 'Initial Contact',
                    'segment': row[10] if len(row) > 10 else 'New',
                    'favorite_strains': row[11] if len(row) > 11 else '',
                    'tags': row[12] if len(row) > 12 else ''
                }

        return None
    except Exception as e:
        print(f"Error getting customer profile: {e}")
        return None

def create_or_update_customer_profile(user_id: str, phone: str = "", name: str = "", order_total: float = 0, attribution_source: str = ""):
    """Create new customer profile or update existing one"""
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return

    try:
        existing = get_customer_profile(user_id)
        now = datetime.now().isoformat()

        if existing:
            # Update existing customer
            total_orders = existing['total_orders'] + (1 if order_total > 0 else 0)
            lifetime_value = existing['lifetime_value'] + order_total

            # Determine segment
            if lifetime_value > 10000:
                segment = 'VIP'
            elif total_orders >= 3:
                segment = 'Repeat'
            elif total_orders == 1:
                segment = 'One-time'
            else:
                segment = 'New'

            # Find and update row
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=GOOGLE_SHEET_ID,
                range='Customers!A:A'
            ).execute()
            rows = result.get('values', [])

            row_index = None
            for i, row in enumerate(rows):
                if row and row[0] == user_id:
                    row_index = i + 1  # Sheets API uses 1-based indexing
                    break

            if row_index:
                update_row = [
                    user_id,
                    phone or existing['phone'],
                    name or existing['name'],
                    existing['first_seen'],
                    now,  # last_seen
                    existing.get('language_preference', 'thai'),  # language_preference
                    total_orders,
                    lifetime_value,
                    existing['acquisition_source'],  # Don't overwrite existing source
                    existing['current_journey_stage'],
                    segment,
                    existing['favorite_strains'],
                    existing['tags']
                ]

                sheets_service.spreadsheets().values().update(
                    spreadsheetId=GOOGLE_SHEET_ID,
                    range=f'Customers!A{row_index}:M{row_index}',
                    valueInputOption='USER_ENTERED',
                    body={'values': [update_row]}
                ).execute()
                print(f"✅ Updated customer profile for {user_id}")
        else:
            # Create new customer with attribution
            source = attribution_source if attribution_source else 'LINE'

            new_row = [
                user_id,
                phone,
                name,
                now,  # first_seen
                now,  # last_seen
                'thai',  # language_preference (default)
                1 if order_total > 0 else 0,  # total_orders
                order_total,  # lifetime_value
                source,  # acquisition_source (captured attribution!)
                'Initial Contact',  # current_journey_stage
                'New',  # segment
                '',  # favorite_strains
                ''  # tags
            ]

            sheets_service.spreadsheets().values().append(
                spreadsheetId=GOOGLE_SHEET_ID,
                range='Customers!A:M',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body={'values': [new_row]}
            ).execute()
            print(f"✅ Created new customer profile for {user_id} (source: {source})")

    except Exception as e:
        print(f"Error creating/updating customer profile: {e}")

def log_message(user_id: str, direction: str, content: str, intent: str = ""):
    """Log message to Messages sheet"""
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return

    try:
        # Get current journey stage
        profile = get_customer_profile(user_id)
        current_stage = profile['current_journey_stage'] if profile else 'Initial Contact'

        row = [
            datetime.now().isoformat(),
            user_id,
            direction,  # 'incoming' or 'outgoing'
            content[:500],  # Limit content length
            intent,
            current_stage,
            current_stage  # Will be updated if stage changes
        ]

        sheets_service.spreadsheets().values().append(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Messages!A:G',
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body={'values': [row]}
        ).execute()

    except Exception as e:
        print(f"Error logging message: {e}")

def extract_customer_info_from_message(message: str) -> dict:
    """
    Smart extraction of customer info (phone, name) from natural conversation
    Returns dict with 'phone' and 'name' if found
    """
    import re

    info = {'phone': None, 'name': None}

    # Phone number patterns (Thai format)
    phone_patterns = [
        r'(?:เบอร์|โทร|เบอ|phone|tel|number)[:\s]*([0-9\-]{9,12})',  # "เบอร์ 092-343-2606"
        r'([0-9]{3}[-\s]?[0-9]{3}[-\s]?[0-9]{4})',  # 092-343-2606 or 0923432606
        r'([0-9]{2}[-\s]?[0-9]{4}[-\s]?[0-9]{4})',  # 09-2343-2606
    ]

    for pattern in phone_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            phone = match.group(1) if len(match.groups()) > 0 else match.group(0)
            # Clean up phone number
            phone = re.sub(r'[^\d]', '', phone)  # Remove non-digits
            if len(phone) >= 9 and len(phone) <= 12:
                # Format to xxx-xxx-xxxx
                if len(phone) == 10:
                    info['phone'] = f"{phone[:3]}-{phone[3:6]}-{phone[6:]}"
                elif len(phone) == 9:
                    info['phone'] = f"{phone[:2]}-{phone[2:6]}-{phone[6:]}"
                else:
                    info['phone'] = phone
                break

    # Name patterns (Thai/English)
    name_patterns = [
        r'(?:my name is|i\'?m)[:\s]+([ก-๙a-zA-Z]{2,30})',  # "My name is Howard"
        r'(?:ชื่อ|called)[:\s]+([ก-๙a-zA-Z\s]{2,30})',  # "ชื่อ จิมมี่"
        r'(?:ผม|ดิฉัน|หนู)[:\s]+([ก-๙a-zA-Z\s]{2,30})',  # "ผม จิมมี่"
    ]

    for pattern in name_patterns:
        match = re.search(pattern, message, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Basic validation
            if len(name) >= 2 and len(name) <= 30:
                info['name'] = name
                break

    return info

def smart_update_customer_profile(user_id: str, message: str):
    """
    Analyzes message for customer info and updates profile if found
    Called on every incoming message
    """
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return

    try:
        # Extract info from message
        extracted = extract_customer_info_from_message(message)

        # Only update if we found something
        if extracted['phone'] or extracted['name']:
            profile = get_customer_profile(user_id)

            # Update with extracted info
            create_or_update_customer_profile(
                user_id=user_id,
                phone=extracted['phone'] or (profile['phone'] if profile else ''),
                name=extracted['name'] or (profile['name'] if profile else ''),
                order_total=0  # Don't increment order count, just update info
            )

            if extracted['phone']:
                print(f"✅ Captured phone from conversation: {extracted['phone']} for user {user_id}")
            if extracted['name']:
                print(f"✅ Captured name from conversation: {extracted['name']} for user {user_id}")

    except Exception as e:
        print(f"Error in smart profile update: {e}")

def detect_language_from_message(message: str) -> Optional[str]:
    """
    Detect EXPLICIT language switch requests only.
    Returns: 'thai', 'english', 'chinese', 'russian', 'japanese', 'korean', 'french', or None

    ONLY triggers on:
    - Language symbols/codes (TH, EN, 中文, RU, 日本語, 한국어, FR)
    - Explicit language commands ('thai', 'english', etc.)

    Does NOT auto-detect from character scripts to avoid false positives.
    """
    # Text-based language switching (check for codes and names)
    message_strip = message.strip()
    message_lower = message.lower().strip()

    # Language code mappings (case-insensitive)
    if message_lower in ['thai', 'ไทย', 'th']:
        return 'thai'
    elif message_lower in ['english', 'en', 'eng']:
        return 'english'
    elif message_strip in ['中文', 'chinese', 'zh', 'cn']:
        return 'chinese'
    elif message_lower in ['russian', 'русский', 'ru', 'rus']:
        return 'russian'
    elif message_strip in ['日本語', 'japanese', 'ja', 'jp'] or message_lower in ['japanese', 'ja', 'jp']:
        return 'japanese'
    elif message_strip in ['한국어', 'korean', 'ko', 'kr'] or message_lower in ['korean', 'ko', 'kr']:
        return 'korean'
    elif message_lower in ['french', 'français', 'francais', 'fr', 'fra']:
        return 'french'

    # NO auto-detection from script - return None
    return None

def update_customer_language(user_id: str, language: str):
    """
    Update customer's language preference in profile
    """
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return

    try:
        profile = get_customer_profile(user_id)
        if profile:
            # Update language preference (column F - index 5)
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=GOOGLE_SHEET_ID,
                range='Customers!A:A'
            ).execute()
            rows = result.get('values', [])

            for i, row in enumerate(rows):
                if row and row[0] == user_id:
                    row_index = i + 1
                    # Update just the language column
                    sheets_service.spreadsheets().values().update(
                        spreadsheetId=GOOGLE_SHEET_ID,
                        range=f'Customers!F{row_index}',
                        valueInputOption='USER_ENTERED',
                        body={'values': [[language]]}
                    ).execute()
                    print(f"✅ Updated language to {language} for user {user_id}")
                    break

    except Exception as e:
        print(f"Error updating language preference: {e}")

def get_greeting_message(language: str = 'thai') -> str:
    """
    Get greeting message with language switching options
    """
    languages = CUSTOMER_CONFIG.get('supported_languages', {})

    if language not in languages:
        language = 'thai'  # Default

    greeting = languages.get(language, {}).get('greeting', 'Welcome to CannaPeace 🌿')

    # Get language switch prompt
    templates = CUSTOMER_CONFIG.get('templates', {})
    lang_switch = templates.get('language_switch_prompt', {}).get(language,
        "🌐 Switch language: 🇹🇭 Thai  |  🇬🇧 English  |  🇨🇳 Chinese")

    return f"{greeting}\n\n{lang_switch}"

# Initialize CRM sheets on startup (with detailed logging)
CRM_SETUP_STATUS = {"success": False, "error": None, "sheets_created": []}
try:
    print("🚀 Initializing CRM sheets on startup...")
    ensure_crm_sheets_exist()
    CRM_SETUP_STATUS["success"] = True
    print("✅ CRM sheets initialization complete")
except Exception as e:
    CRM_SETUP_STATUS["error"] = str(e)
    print(f"⚠️ Could not initialize CRM sheets: {e}")
    import traceback
    traceback.print_exc()

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
    import time
    start_time = time.time()
    timings = {}

    try:
        message_text = event.message.text
        user_id = event.source.user_id if hasattr(event.source, 'user_id') else "demo_user"

        print(f"⏱️ [PERF] Message received from {user_id}: '{message_text[:50]}...'")

        # v2.0: Log incoming message
        log_message(user_id, 'incoming', message_text)

        # v2.0: Check if this is first message BEFORE creating profile
        profile = get_customer_profile(user_id)
        is_first_message = not profile

        # v2.0: Create/update customer profile on first contact
        if not profile:
            create_or_update_customer_profile(user_id)
            profile = get_customer_profile(user_id)  # Reload profile after creation

        # v2.0: Smart extraction - capture phone/name from conversation
        smart_update_customer_profile(user_id, message_text)

        # v2.0: Language detection and switching
        detected_language = detect_language_from_message(message_text)
        if detected_language:
            update_customer_language(user_id, detected_language)
            # Send confirmation in new language
            templates = CUSTOMER_CONFIG.get('templates', {})
            confirmation_msg = templates.get('language_switch_confirmation', {}).get(
                detected_language,
                '✅ Language updated!'
            )

            if line_bot_api:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=confirmation_msg)
                )
            return  # Don't process further, just acknowledge language change

        # Get customer's language preference
        current_language = profile.get('language_preference', 'thai') if profile else 'thai'

        # Send greeting on first message only
        if is_first_message:
            greeting = get_greeting_message(current_language)
            if line_bot_api:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text=greeting)
                )
            return

        # Show typing indicator immediately
        if line_bot_api and hasattr(event.source, 'user_id'):
            try:
                line_bot_api.show_loading_animation(event.source.user_id)
            except Exception as typing_error:
                print(f"⚠️ Could not show typing indicator: {typing_error}")

        # Check if Claude is configured
        if not anthropic_client:
            if line_bot_api:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ DEMO MODE - Claude AI not configured")
                )
            return

        # Load conversation history
        prep_start = time.time()
        if user_id not in conversation_memory:
            conversation_memory[user_id] = []

        conversation_history = conversation_memory[user_id]

        # Build conversation context
        history_text = ""
        if conversation_history:
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in conversation_history[-MAX_CONVERSATION_HISTORY:]])

        # Load product catalog
        config = json.loads(Path("customer_config.json").read_text())
        timings['prep'] = time.time() - prep_start
        products_info = "\n".join([
            f"- {p['name_english']}{' ('+p['alias']+')' if 'alias' in p else ''} ({p['name_thai']}): {p['strain_type']} | {p['thc']} THC | {p['description']}"
            for p in config["products"]
        ])

        # Language instruction based on customer preference
        language_instructions = {
            'thai': "RESPOND IN THAI (ตอบเป็นภาษาไทย). Be polite and use ค่ะ/ครับ.",
            'english': "RESPOND IN ENGLISH. Be friendly and professional.",
            'chinese': "RESPOND IN CHINESE (用中文回复). Be polite and professional.",
            'russian': "RESPOND IN RUSSIAN (Отвечайте на русском). Be polite and professional.",
            'japanese': "RESPOND IN JAPANESE (日本語で応答してください). Be polite and use です/ます.",
            'korean': "RESPOND IN KOREAN (한국어로 응답하세요). Be polite and use 요/습니다.",
            'french': "RESPOND IN FRENCH (Répondez en français). Be polite and professional."
        }
        lang_instruction = language_instructions.get(current_language, language_instructions['english'])

        # Conversational AI prompt
        prompt = f"""You are a friendly customer service agent for CannaPeace (แคนนาพีซ / 大麻和平), a premium cannabis shop in Thailand.

**LANGUAGE:** {lang_instruction}

CONVERSATION HISTORY:
{history_text if history_text else "(New conversation)"}

CUSTOMER'S NEW MESSAGE:
{message_text}

YOUR PRODUCTS:
{products_info}

YOUR ROLE:
1. If greeting (hi/hello/สวัสดี/你好) → Greet warmly in customer's language
2. If asking about menu/products (what do you have/menu/รายการ) → Show the menu with short descriptions
3. If asking about SPECIFIC strain → Say "SEND_IMAGE:strain_name" then describe it in detail
4. If placing an order:
   - Extract items and quantities
   - Ask for PHONE NUMBER if not provided
   - Ask for DELIVERY ADDRESS if not provided
   - When ALL info complete, confirm order

MENU FORMAT (when showing menu):
🌿 **CannaPeace Menu** 🌿

1. Miracle Mints (Cap Junky) - Hybrid 28% THC - Sweet, relaxing
2. Alien Marker - Indica 26% THC - Deep relaxation
3. Tropical Cherry (Trop Cherry) - Hybrid 27% THC - Tropical, fruity
4. Gogurtz - Hybrid 29% THC - Creamy, dessert
5. Berry Bonds - Indica 25% THC - Berry, evening
6. Any Day (LCG x Grapegas) - Hybrid 30% THC - Gassy, strong
7. Apple Banana - Sativa 24% THC - Uplifting, fruity

💬 Ask about any strain for details!

IMPORTANT STRAIN NAME ALIASES (use these for SEND_IMAGE):
- "Miracle Mints" OR "Cap Junky" → Use "SEND_IMAGE:Miracle Mints"
- "Any Day" OR "LCG x Grapegas" → Use "SEND_IMAGE:Any Day"
- "Tropical Cherry" OR "Trop Cherry" → Use "SEND_IMAGE:Tropical Cherry"
- All others → Use exact name from menu

WHEN USER ASKS ABOUT SPECIFIC STRAIN:
- Respond with: SEND_IMAGE:mapped_name (use aliases above)
- Then describe the strain

- When order is COMPLETE (has phone + address):
  ORDER_COMPLETE:{{"customer_name": "...", "phone": "...", "address": "...", "items": [{{"name": "...", "quantity": "X grams"}}]}}

NOTE: Do NOT mention prices. Prices are discussed privately/in person.

Respond now:"""

        # Call Claude
        claude_start = time.time()
        response = anthropic_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1500,
            messages=[{"role": "user", "content": prompt}]
        )
        timings['claude_api'] = time.time() - claude_start

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

                # Save to Google Sheets (v2.0 CRM)
                if sheets_service and GOOGLE_SHEET_ID != "DEMO_SHEET":
                    sheets_start = time.time()
                    items_str = ", ".join([f"{item['name']} {item['quantity']}" for item in order_data["items"]])

                    # v2.0: Save order with LINE User ID
                    order_row = [
                        datetime.now().isoformat(),
                        user_id,  # LINE_User_ID
                        order_data.get("customer_name", "Customer"),
                        order_data.get("phone", "Not provided"),
                        items_str,
                        "TBD",  # Total - discussed privately
                        order_data.get("address", ""),
                        "Pending",  # Status
                        "LINE"  # Attribution_Source (default to LINE for now)
                    ]

                    body = {'values': [order_row]}
                    sheets_service.spreadsheets().values().append(
                        spreadsheetId=GOOGLE_SHEET_ID,
                        range='Orders!A:I',  # v2.0: Updated range with new columns
                        valueInputOption='USER_ENTERED',
                        insertDataOption='INSERT_ROWS',
                        body=body
                    ).execute()

                    # v2.0: Create or update customer profile (increment order count)
                    create_or_update_customer_profile(
                        user_id=user_id,
                        phone=order_data.get("phone", ""),
                        name=order_data.get("customer_name", ""),
                        order_total=1  # Just increment order count, no price tracking
                    )

                    timings['google_sheets'] = time.time() - sheets_start

                    print(f"✅ Order saved + customer profile updated for {user_id}")

                # Clear conversation after successful order
                conversation_memory[user_id] = []

            except Exception as sheet_error:
                print(f"Sheet error: {sheet_error}")

        # Check if bot wants to send product image
        image_to_send = None
        if "SEND_IMAGE:" in bot_reply:
            img_start = time.time()
            try:
                # Extract strain name
                image_marker = "SEND_IMAGE:"
                start_idx = bot_reply.index(image_marker) + len(image_marker)
                end_idx = bot_reply.index("\n", start_idx) if "\n" in bot_reply[start_idx:] else len(bot_reply)
                strain_name = bot_reply[start_idx:end_idx].strip()

                # Find product image URL using real strain images from product_images/v6/
                # Image filenames match display names (e.g., "Alien Marker.png")

                # Name mappings for strain variations (same strain, different names)
                name_mappings = {
                    # Tropical Cherry variations
                    "trop cherry": "Tropical Cherry",
                    "tropical cherry": "Tropical Cherry",

                    # Cap Junky = Miracle Mints (same strain)
                    "cap junky": "Miracle Mints",
                    "capjunky": "Miracle Mints",
                    "miracle mints": "Miracle Mints",

                    # LCG x Grapegas = Any Day (same strain)
                    "lcg x grapegas": "Any Day",
                    "lcg grapegas": "Any Day",
                    "lcgxgrapegas": "Any Day",
                    "any day": "Any Day",
                    "anyday": "Any Day"
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
                timings['image_processing'] = time.time() - img_start

            except Exception as img_error:
                print(f"Image error: {img_error}")
                import traceback
                traceback.print_exc()
                timings['image_processing'] = time.time() - img_start

        # Send reply (image + text if applicable)
        if line_bot_api:
            line_start = time.time()
            messages = []

            # Add image if requested
            if image_to_send:
                messages.append(ImageSendMessage(
                    original_content_url=image_to_send,
                    preview_image_url=image_to_send
                ))

            # Add text reply
            messages.append(TextSendMessage(text=bot_reply))

            # v2.0: Log outgoing message
            log_message(user_id, 'outgoing', bot_reply)

            line_bot_api.reply_message(event.reply_token, messages)
            timings['line_api'] = time.time() - line_start

        # Log performance summary
        total_time = time.time() - start_time
        timings['total'] = total_time
        print(f"⏱️ [PERF] Total: {total_time:.2f}s | " +
              " | ".join([f"{k}: {v:.2f}s" for k, v in timings.items() if k != 'total']))

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
        "product_images_count": images_count,
        "crm_setup_status": CRM_SETUP_STATUS
    }

@app.get("/setup-crm")
async def setup_crm_manual():
    """
    Manual trigger for CRM sheets setup
    Use this if sheets weren't auto-created on startup
    Safe to run multiple times (idempotent)
    """
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return {
            "success": False,
            "error": "Google Sheets not configured. Check GOOGLE_CREDENTIALS_BASE64 and GOOGLE_SHEET_ID environment variables.",
            "google_sheet_id": GOOGLE_SHEET_ID
        }

    try:
        # Get current sheets before setup
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=GOOGLE_SHEET_ID).execute()
        sheets_before = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]

        # Run setup
        ensure_crm_sheets_exist()

        # Get sheets after setup
        sheet_metadata = sheets_service.spreadsheets().get(spreadsheetId=GOOGLE_SHEET_ID).execute()
        sheets_after = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]

        new_sheets = [s for s in sheets_after if s not in sheets_before]

        return {
            "success": True,
            "sheets_before": sheets_before,
            "sheets_after": sheets_after,
            "new_sheets_created": new_sheets,
            "message": "CRM setup completed successfully",
            "google_sheet_url": f"https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit"
        }

    except Exception as e:
        import traceback
        return {
            "success": False,
            "error": str(e),
            "traceback": traceback.format_exc(),
            "google_sheet_id": GOOGLE_SHEET_ID
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

# ============================================================================
# ATTRIBUTION TRACKING SYSTEM
# ============================================================================

# In-memory attribution tracking (will be stored in Google Sheets)
attribution_tracking = {}

@app.get("/admin/links", response_class=HTMLResponse)
async def attribution_link_generator():
    """Admin page to create and manage attribution tracking links"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CannaPeace - Attribution Link Generator</title>
        <meta charset="UTF-8">
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Arial, sans-serif;
                max-width: 900px;
                margin: 40px auto;
                padding: 20px;
                background: #f5f5f5;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 12px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }
            h1 { color: #2c5f2d; margin-top: 0; }
            h2 { color: #555; margin-top: 30px; }
            .form-group {
                margin: 20px 0;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
                color: #333;
            }
            input, select {
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 6px;
                font-size: 14px;
                box-sizing: border-box;
            }
            button {
                background: #2c5f2d;
                color: white;
                padding: 12px 24px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
            }
            button:hover { background: #1e4620; }
            .result {
                margin-top: 20px;
                padding: 15px;
                background: #f0f8f0;
                border: 1px solid #2c5f2d;
                border-radius: 6px;
                display: none;
            }
            .result.show { display: block; }
            .link-box {
                background: white;
                padding: 12px;
                border: 2px solid #2c5f2d;
                border-radius: 6px;
                font-family: monospace;
                word-break: break-all;
                margin: 10px 0;
            }
            .copy-btn {
                background: #4a90e2;
                padding: 8px 16px;
                margin-top: 10px;
                font-size: 14px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 20px;
            }
            .stat-card {
                background: #f9f9f9;
                padding: 15px;
                border-radius: 8px;
                border-left: 4px solid #2c5f2d;
            }
            .stat-label { font-size: 12px; color: #666; }
            .stat-value { font-size: 24px; font-weight: bold; color: #2c5f2d; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🔗 Attribution Link Generator</h1>
            <p>Create tracking links to measure which channels drive customers to CannaPeace.</p>

            <h2>Create New Tracking Link</h2>
            <div class="form-group">
                <label>Channel / Platform</label>
                <select id="channel">
                    <option value="tiktok">TikTok</option>
                    <option value="instagram">Instagram</option>
                    <option value="facebook">Facebook</option>
                    <option value="twitter">Twitter/X</option>
                    <option value="youtube">YouTube</option>
                    <option value="line">LINE</option>
                    <option value="google">Google Ads</option>
                    <option value="email">Email</option>
                    <option value="qr">QR Code</option>
                    <option value="other">Other</option>
                </select>
            </div>

            <div class="form-group">
                <label>Campaign Name (e.g., "summer2024", "newyear")</label>
                <input type="text" id="campaign" placeholder="summer2024">
            </div>

            <div class="form-group">
                <label>Medium (optional)</label>
                <select id="medium">
                    <option value="social">Social Media</option>
                    <option value="paid">Paid Ad</option>
                    <option value="organic">Organic</option>
                    <option value="referral">Referral</option>
                    <option value="email">Email</option>
                    <option value="offline">Offline</option>
                </select>
            </div>

            <button onclick="generateLink()">🎯 Generate Tracking Link</button>

            <div class="result" id="result">
                <h3>✅ Link Created!</h3>
                <p><strong>Your Tracking Link:</strong></p>
                <div class="link-box" id="generatedLink"></div>
                <button class="copy-btn" onclick="copyLink()">📋 Copy Link</button>

                <p style="margin-top: 20px; font-size: 13px; color: #666;">
                    <strong>How to use:</strong><br>
                    1. Copy and share this link on your chosen platform (TikTok, Instagram, etc.)<br>
                    2. When customers click, they'll be redirected directly to your LINE bot<br>
                    3. The click and source will be automatically tracked<br>
                    4. When they message the bot, their attribution is captured<br>
                    5. View analytics below to see which channels perform best
                </p>
            </div>

            <h2>📊 Quick Stats</h2>
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-label">Total Links Created</div>
                    <div class="stat-value" id="totalLinks">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Clicks</div>
                    <div class="stat-value" id="totalClicks">-</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Conversions</div>
                    <div class="stat-value" id="totalConversions">-</div>
                </div>
            </div>
        </div>

        <script>
            let currentLink = '';

            async function generateLink() {
                const channel = document.getElementById('channel').value;
                const campaign = document.getElementById('campaign').value;
                const medium = document.getElementById('medium').value;

                if (!campaign) {
                    alert('Please enter a campaign name');
                    return;
                }

                try {
                    const response = await fetch('/api/create-link', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({ channel, campaign, medium })
                    });

                    const data = await response.json();

                    document.getElementById('generatedLink').textContent = data.tracking_link;
                    document.getElementById('result').classList.add('show');

                    currentLink = data.tracking_link;

                    loadStats();
                } catch (error) {
                    alert('Error creating link: ' + error.message);
                }
            }

            function copyLink() {
                navigator.clipboard.writeText(currentLink);
                alert('✅ Tracking link copied! Share it on ' + document.getElementById('channel').options[document.getElementById('channel').selectedIndex].text);
            }

            async function loadStats() {
                try {
                    const response = await fetch('/api/attribution-stats');
                    const data = await response.json();

                    document.getElementById('totalLinks').textContent = data.total_links;
                    document.getElementById('totalClicks').textContent = data.total_clicks;
                    document.getElementById('totalConversions').textContent = data.total_conversions;
                } catch (error) {
                    console.error('Error loading stats:', error);
                }
            }

            // Load stats on page load
            loadStats();
        </script>
    </body>
    </html>
    """

@app.post("/api/create-link")
async def create_attribution_link(request: Request):
    """Create a new attribution tracking link"""
    data = await request.json()
    channel = data.get('channel', 'unknown')
    campaign = data.get('campaign', 'default')
    medium = data.get('medium', 'social')

    # Generate unique link ID
    import hashlib
    import time
    link_id = hashlib.md5(f"{channel}_{campaign}_{time.time()}".encode()).hexdigest()[:8].upper()

    # Get base URL
    base_url = os.getenv("PUBLIC_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000"))
    if not base_url.startswith("http"):
        base_url = f"https://{base_url}"

    # Create tracking link
    tracking_link = f"{base_url}/join?source={channel}&campaign={campaign}&medium={medium}&ref={link_id}"

    # LINE Official Account URL (replace with your actual LINE bot link)
    line_bot_id = os.getenv("LINE_BOT_ID", "@cannapeace")  # Your LINE@ ID
    line_link = f"https://line.me/R/ti/p/{line_bot_id}?ref={link_id}"

    # Save to Google Sheets (Attribution_Links)
    if sheets_service and GOOGLE_SHEET_ID != "DEMO_SHEET":
        try:
            link_row = [
                link_id,
                channel,
                campaign,
                medium,
                f"{channel}_{campaign}",  # UTM_Source
                0,  # Total_Clicks
                0,  # Total_Conversions
                0,  # Revenue
                datetime.now().isoformat()
            ]

            body = {'values': [link_row]}
            sheets_service.spreadsheets().values().append(
                spreadsheetId=GOOGLE_SHEET_ID,
                range='Attribution_Links!A:I',
                valueInputOption='USER_ENTERED',
                insertDataOption='INSERT_ROWS',
                body=body
            ).execute()
            print(f"✅ Created attribution link: {link_id} for {channel}/{campaign}")
        except Exception as e:
            print(f"⚠️ Error saving attribution link: {e}")

    return {
        "success": True,
        "link_id": link_id,
        "tracking_link": tracking_link,
        "line_link": line_link,
        "channel": channel,
        "campaign": campaign,
        "medium": medium
    }

@app.get("/join")
async def join_redirect(source: str = "direct", campaign: str = "none", medium: str = "unknown", ref: str = ""):
    """Redirect directly to LINE bot while capturing attribution"""
    from fastapi.responses import RedirectResponse

    # Track click in Google Sheets
    if sheets_service and GOOGLE_SHEET_ID != "DEMO_SHEET" and ref:
        try:
            # Update click count for this link
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=GOOGLE_SHEET_ID,
                range='Attribution_Links!A:G'
            ).execute()
            rows = result.get('values', [])

            for i, row in enumerate(rows[1:], start=2):  # Skip header
                if row and row[0] == ref:
                    current_clicks = int(row[5]) if len(row) > 5 and row[5] else 0
                    sheets_service.spreadsheets().values().update(
                        spreadsheetId=GOOGLE_SHEET_ID,
                        range=f'Attribution_Links!F{i}',
                        valueInputOption='USER_ENTERED',
                        body={'values': [[current_clicks + 1]]}
                    ).execute()
                    print(f"✅ Tracked click for link {ref} (source: {source}, campaign: {campaign})")
                    break
        except Exception as e:
            print(f"⚠️ Error tracking click: {e}")

    # Store attribution for when user contacts bot
    attribution_tracking[ref] = {
        "source": source,
        "campaign": campaign,
        "medium": medium,
        "ref_id": ref,
        "timestamp": datetime.now().isoformat()
    }

    # Redirect directly to LINE bot
    line_bot_id = os.getenv("LINE_BOT_ID", "@cannapeace")
    line_url = f"https://line.me/R/ti/p/{line_bot_id}"

    return RedirectResponse(url=line_url, status_code=302)

@app.get("/api/attribution-stats")
async def get_attribution_stats():
    """Get attribution analytics"""
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return {
            "total_links": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "links": []
        }

    try:
        # Get attribution links
        result = sheets_service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Attribution_Links!A:I'
        ).execute()
        rows = result.get('values', [])

        if len(rows) <= 1:
            return {
                "total_links": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "links": []
            }

        links = []
        total_clicks = 0
        total_conversions = 0

        for row in rows[1:]:  # Skip header
            if row:
                clicks = int(row[5]) if len(row) > 5 and row[5] else 0
                conversions = int(row[6]) if len(row) > 6 and row[6] else 0

                total_clicks += clicks
                total_conversions += conversions

                links.append({
                    "link_id": row[0] if len(row) > 0 else "",
                    "channel": row[1] if len(row) > 1 else "",
                    "campaign": row[2] if len(row) > 2 else "",
                    "clicks": clicks,
                    "conversions": conversions
                })

        return {
            "total_links": len(rows) - 1,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "links": sorted(links, key=lambda x: x['clicks'], reverse=True)
        }

    except Exception as e:
        print(f"Error getting attribution stats: {e}")
        return {
            "total_links": 0,
            "total_clicks": 0,
            "total_conversions": 0,
            "links": [],
            "error": str(e)
        }

# ============================================================================
# END ATTRIBUTION SYSTEM
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Restaurant LINE-to-Excel Bridge (Demo)")
    print(f"📍 Open: http://localhost:8001")
    print(f"🔧 Mode: {'DEMO' if not anthropic_client else 'LIVE'}")
    uvicorn.run(app, host="0.0.0.0", port=8001)
