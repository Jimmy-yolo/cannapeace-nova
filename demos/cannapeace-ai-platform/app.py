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
from linebot.models import (
    MessageEvent, FollowEvent, PostbackEvent,
    TextMessage, TextSendMessage, ImageSendMessage, AudioSendMessage,
    QuickReply, QuickReplyButton, PostbackAction, MessageAction
)
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

# Strain menu for Quick Reply buttons
STRAIN_MENU = [
    {"name": "Miracle Mints", "emoji": "🍬"},
    {"name": "Alien Marker", "emoji": "👽"},
    {"name": "Tropical Cherry", "emoji": "🍒"},
    {"name": "Gogurtz", "emoji": "🍰"},
    {"name": "Berry Bonds", "emoji": "🫐"},
    {"name": "Any Day", "emoji": "⛽"},
    {"name": "Apple Banana", "emoji": "🍎"}
]

def create_menu_quick_reply():
    """Create Quick Reply buttons for strain menu"""
    quick_reply_buttons = []
    for strain in STRAIN_MENU:
        button = QuickReplyButton(
            action=PostbackAction(
                label=f"{strain['emoji']} {strain['name']}",
                data=f"strain_info:{strain['name']}",
                display_text=strain['name']
            )
        )
        quick_reply_buttons.append(button)
    return QuickReply(items=quick_reply_buttons)

def create_language_quick_reply():
    """Create COMPACT Quick Reply buttons for language selection (small buttons = more fit on screen!)"""
    languages = [
        {"code": "thai", "label": "🇹🇭", "display": "ไทย"},
        {"code": "english", "label": "🇬🇧", "display": "English"},
        {"code": "chinese", "label": "🇨🇳", "display": "中文"},
        {"code": "russian", "label": "🇷🇺", "display": "Русский"},
        {"code": "japanese", "label": "🇯🇵", "display": "日本語"},
        {"code": "korean", "label": "🇰🇷", "display": "한국어"},
        {"code": "french", "label": "🇫🇷", "display": "Français"}
    ]

    quick_reply_buttons = []
    for lang in languages:
        button = QuickReplyButton(
            action=PostbackAction(
                label=lang['label'],  # Just flag emoji - compact!
                data=f"language:{lang['code']}",
                display_text=lang['display']  # Full language name appears in chat
            )
        )
        quick_reply_buttons.append(button)

    return QuickReply(items=quick_reply_buttons)

def create_age_gate_quick_reply():
    """Create Quick Reply buttons for age verification"""
    buttons = [
        QuickReplyButton(
            action=PostbackAction(
                label="✅ Yes, I'm 20+",
                data="age_verified:yes",
                display_text="Yes, I'm over 20 years old"
            )
        ),
        QuickReplyButton(
            action=PostbackAction(
                label="❌ No, I'm under 20",
                data="age_verified:no",
                display_text="No, I'm under 20 years old"
            )
        )
    ]
    return QuickReply(items=buttons)

def get_age_gate_message(language: str = 'thai') -> str:
    """Get age gate message in customer's language"""
    messages = {
        'thai': """🔞 **ยืนยันอายุ / Age Verification**

ตามกฎหมายไทย กัญชาสามารถจำหน่ายได้เฉพาะบุคคลที่มีอายุ 20 ปีขึ้นไปเท่านั้น

**CannaPeace จำหน่ายกัญชาเพื่อ:**
• การบำบัดแบบดั้งเดิม (Traditional therapy)
• การใช้งานส่วนบุคคล (Personal use)

⚠️ **ข้อกำหนด:**
• ห้ามขายให้ผู้ที่อายุต่ำกว่า 20 ปี
• ห้ามขายให้สตรีมีครรภ์หรือให้นมบุตร
• ใช้อย่างมีความรับผิดชอบ

📄 อ่านข้อกำหนดและเงื่อนไขฉบับเต็ม: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

**คุณมีอายุ 20 ปีขึ้นไปหรือไม่?**""",

        'english': """🔞 **Age Verification**

Under Thai law, cannabis may only be sold to individuals aged 20 years or older.

**CannaPeace sells cannabis for:**
• Traditional therapy
• Personal use

⚠️ **Requirements:**
• Must be 20 years or older
• Not for pregnant or breastfeeding women
• Use responsibly

📄 Read full Terms & Conditions: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

**Are you 20 years of age or older?**""",

        'chinese': """🔞 **年龄验证**

根据泰国法律，大麻只能出售给20岁或以上的人士。

**CannaPeace 销售大麻用于:**
• 传统疗法
• 个人使用

⚠️ **要求：**
• 必须年满20岁
• 不适用于孕妇或哺乳期妇女
• 负责任地使用

📄 阅读完整条款和条件: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

**您是否年满20岁？**""",

        'russian': """🔞 **Подтверждение возраста**

В соответствии с законодательством Таиланда, каннабис может продаваться только лицам в возрасте 20 лет и старше.

**CannaPeace продает каннабис для:**
• Традиционной терапии
• Личного использования

⚠️ **Требования:**
• Возраст 20 лет и старше
• Не для беременных и кормящих женщин
• Используйте ответственно

📄 Полные условия: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

**Вам 20 лет или больше?**""",

        'japanese': """🔞 **年齢確認**

タイの法律により、大麻は20歳以上の方にのみ販売できます。

**CannaPeaceは以下の用途で大麻を販売しています：**
• 伝統的な治療
• 個人使用

⚠️ **要件：**
• 20歳以上であること
• 妊娠中または授乳中の方には販売できません
• 責任を持って使用してください

📄 利用規約の全文: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

**あなたは20歳以上ですか？**""",

        'korean': """🔞 **연령 확인**

태국 법에 따라 대마초는 20세 이상인 사람에게만 판매할 수 있습니다.

**CannaPeace는 다음 용도로 대마초를 판매합니다:**
• 전통 요법
• 개인 사용

⚠️ **요구 사항:**
• 20세 이상이어야 함
• 임산부 또는 수유 중인 여성 불가
• 책임감 있게 사용하십시오

📄 전체 이용약관 읽기: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

**귀하는 20세 이상입니까?**""",

        'french': """🔞 **Vérification de l'âge**

Selon la loi thaïlandaise, le cannabis ne peut être vendu qu'aux personnes âgées de 20 ans ou plus.

**CannaPeace vend du cannabis pour:**
• Thérapie traditionnelle
• Usage personnel

⚠️ **Exigences:**
• Avoir 20 ans ou plus
• Pas pour les femmes enceintes ou allaitantes
• Utiliser de manière responsable

📄 Lire les conditions générales complètes: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

**Avez-vous 20 ans ou plus?**"""
    }
    return messages.get(language, messages['thai'])

def get_nancy_welcome(language: str = 'thai') -> str:
    """Get Nancy's short, natural welcome message (accompanies voice greeting)"""
    messages = {
        'thai': """สวัสดีค่ะ! ฉันชื่อ Nancy 🌿

มีอะไรให้ช่วยไหมคะวันนี้? 😊
พิมพ์ "ดูเมนู" ถ้าอยากดูสายพันธุ์กัญชาทั้งหมดค่ะ""",

        'english': """Hey! I'm Nancy 🌿

What can I help you with today? 😊
Type "menu" to see all our cannabis strains!""",

        'chinese': """你好！我是Nancy 🌿

今天有什么可以帮您的吗？😊
输入"菜单"查看所有大麻品种！""",

        'russian': """Привет! Я Nancy 🌿

Чем могу помочь сегодня? 😊
Напишите "меню" чтобы увидеть все сорта!""",

        'japanese': """こんにちは！私はNancyです 🌿

今日は何かお手伝いできますか？😊
「メニュー」と入力して全品種をご覧ください！""",

        'korean': """안녕하세요! 저는 Nancy입니다 🌿

오늘 무엇을 도와드릴까요? 😊
"메뉴"를 입력하여 모든 품종을 확인하세요!""",

        'french': """Salut! Je suis Nancy 🌿

Comment puis-je vous aider aujourd'hui? 😊
Tapez "menu" pour voir toutes nos variétés!"""
    }
    return messages.get(language, messages['thai'])

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

def update_customer_age_verified(user_id: str, verified: bool):
    """
    Update customer's age verification status in profile
    Column N (index 13) - Age_Verified
    """
    if not sheets_service or GOOGLE_SHEET_ID == "DEMO_SHEET":
        return

    try:
        profile = get_customer_profile(user_id)
        if profile:
            # Update age_verified field (column N - index 13)
            result = sheets_service.spreadsheets().values().get(
                spreadsheetId=GOOGLE_SHEET_ID,
                range='Customers!A:A'
            ).execute()
            rows = result.get('values', [])

            for i, row in enumerate(rows):
                if row and row[0] == user_id:
                    row_index = i + 1
                    # Update age_verified column
                    age_status = "Yes" if verified else "No"
                    sheets_service.spreadsheets().values().update(
                        spreadsheetId=GOOGLE_SHEET_ID,
                        range=f'Customers!N{row_index}',
                        valueInputOption='USER_ENTERED',
                        body={'values': [[age_status]]}
                    ).execute()
                    print(f"✅ Updated age_verified to {age_status} for user {user_id}")
                    break

    except Exception as e:
        print(f"Error updating age verification: {e}")

def get_first_contact_welcome() -> str:
    """
    Get GLOBAL welcome message for first contact (Follow Event or First Message)
    Shows all language greetings to feel welcoming and international
    """
    return """สวัสดี / Hello / 你好 / Привет / こんにちは / 안녕하세요 / Bonjour

🌿 **ยินดีต้อนรับสู่ CannaPeace!**

ฉันเป็นแชทบอท AI ที่พร้อมช่วยคุณตลอด 24/7:
• เมนูสายพันธุ์กัญชาและข้อมูล
• คำแนะนำเฉพาะบุคคล
• สั่งซื้อง่ายๆ
• ตอบคำถามทุกเรื่อง

💬 **เลือกภาษาของคุณ:**
👇 กดธงด้านล่างเลย!"""

def get_welcome_message(language: str = 'thai') -> str:
    """
    Get language-specific welcome message (used after language is selected)
    Emphasizes it's an interactive chatbot, not a broadcast channel
    """
    welcome_messages = {
        'thai': """🌿 สวัสดีค่ะ! ยินดีต้อนรับสู่ CannaPeace

ฉันเป็นแชทบอท AI ที่พร้อมช่วยคุณตลอด 24/7! 💬

🎯 ฉันช่วยอะไรคุณได้บ้าง?
• ดูเมนูสายพันธุ์กัญชาทั้งหมด
• แนะนำสายพันธุ์ที่เหมาะกับคุณ
• สั่งสินค้า (ง่ายมาก!)
• ตอบคำถามทุกเรื่อง

💬 แค่พิมพ์คุยมาได้เลย! เช่น:
"ดูเมนู" | "แนะนำหน่อย" | "สั่งของ"

มีอะไรให้ช่วยไหมคะ? 😊""",

        'english': """🌿 Hey! Welcome to CannaPeace

I'm your AI chatbot assistant, here 24/7! 💬

🎯 How can I help you?
• Browse our full strain menu
• Get personalized recommendations
• Place orders (super easy!)
• Answer any questions

💬 Just chat with me! Try:
"Show menu" | "Recommend" | "Order"

🌐 **Switch Language:**
TH | EN | 中文 | RU | 日本語 | 한국어 | FR

What can I help you with today? 😊""",

        'chinese': """🌿 嗨！欢迎来到 CannaPeace

我是您的 AI 聊天机器人助手，24/7 在线！💬

🎯 我能帮您什么？
• 浏览完整的品种菜单
• 获得个性化推荐
• 下订单（超简单！）
• 回答任何问题

💬 直接和我聊天！试试：
"显示菜单" | "推荐" | "订购"

🌐 **切换语言:**
TH | EN | 中文 | RU | 日本語 | 한국어 | FR

今天需要什么帮助？😊""",

        'russian': """🌿 Привет! Добро пожаловать в CannaPeace

Я ваш AI чат-бот помощник, доступен 24/7! 💬

🎯 Чем могу помочь?
• Посмотреть меню всех сортов
• Получить персональные рекомендации
• Оформить заказ (очень просто!)
• Ответить на любые вопросы

💬 Просто напишите мне! Попробуйте:
"Меню" | "Посоветуй" | "Заказать"

🌐 **Сменить язык:**
TH | EN | 中文 | RU | 日本語 | 한국語 | FR

Чем могу помочь сегодня? 😊""",

        'japanese': """🌿 こんにちは！CannaPeaceへようこそ

私はあなたの AI チャットボットアシスタントです。24時間対応！💬

🎯 どのようにお手伝いできますか？
• 全品種メニューを閲覧
• パーソナライズされた推奨
• 注文（とても簡単！）
• あらゆる質問に回答

💬 チャットしてください！試してみて：
"メニュー表示" | "おすすめ" | "注文"

🌐 **言語切り替え:**
TH | EN | 中文 | RU | 日本語 | 한국어 | FR

今日は何かお手伝いできますか？😊""",

        'korean': """🌿 안녕하세요! CannaPeace에 오신 것을 환영합니다

저는 24시간 이용 가능한 AI 챗봇 도우미입니다! 💬

🎯 어떻게 도와드릴까요?
• 전체 품종 메뉴 보기
• 맞춤 추천받기
• 주문하기 (아주 쉬워요!)
• 모든 질문에 답변

💬 채팅하세요! 예시:
"메뉴 보기" | "추천" | "주문"

🌐 **언어 전환:**
TH | EN | 中文 | RU | 日本語 | 한국어 | FR

오늘 무엇을 도와드릴까요? 😊""",

        'french': """🌿 Salut ! Bienvenue à CannaPeace

Je suis votre assistant chatbot AI, disponible 24/7 ! 💬

🎯 Comment puis-je vous aider ?
• Parcourir le menu complet
• Obtenir des recommandations personnalisées
• Passer commande (super facile !)
• Répondre à toutes vos questions

💬 Chattez avec moi ! Essayez :
"Menu" | "Recommander" | "Commander"

🌐 **Changer de langue :**
TH | EN | 中文 | RU | 日本語 | 한국어 | FR

Que puis-je faire pour vous aujourd'hui ? 😊"""
    }

    return welcome_messages.get(language, welcome_messages['thai'])

def get_greeting_message(language: str = 'thai') -> str:
    """
    Get greeting message with language switching options
    (Used when customer sends first message)
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
        <title>CannaPeace AI Platform - DEMO MODE</title>
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
        <h1>🌿 CannaPeace AI Platform</h1>
        <div style="background: #fff3cd; padding: 10px; margin: 10px 0; border-left: 4px solid #ffc107; border-radius: 4px;">
            <strong>⚠️ DEMO MODE:</strong> Using sample data. Connect LINE bot + Google Sheets for live operation.
        </div>
        <p><strong>AI-powered customer service with multilingual support (7 languages)</strong></p>

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

        # Send greeting on first message only (text only, voice comes after age gate)
        if is_first_message:
            if line_bot_api:
                # Global welcome message with language Quick Reply
                welcome_text = get_first_contact_welcome()
                text_message = TextSendMessage(text=welcome_text)
                text_message.quick_reply = create_language_quick_reply()  # Language selection buttons

                line_bot_api.reply_message(event.reply_token, text_message)
            return

        # CHECK AGE VERIFICATION (Block underage users)
        age_verified = profile.get('age_verified', None) if profile else None

        if age_verified == "No":  # Explicitly marked as underage
            # Block from using the bot
            blocked_messages = {
                'thai': "ขออภัยค่ะ 🌿\n\nตามกฎหมายไทย เราไม่สามารถให้บริการผู้ที่อายุต่ำกว่า 20 ปีค่ะ\n\nหวังว่าจะได้พบคุณอีกครั้งเมื่อคุณมีอายุครบ 20 ปีนะคะ!",
                'english': "Sorry! 🌿\n\nUnder Thai law, we cannot serve customers under 20 years old.\n\nHope to see you when you turn 20!",
                'chinese': "抱歉！🌿\n\n根据泰国法律，我们不能为20岁以下的客户提供服务。\n\n希望您20岁时再见！",
                'russian': "Извините! 🌿\n\nСогласно законам Таиланда, мы не можем обслуживать клиентов младше 20 лет.\n\nНадеемся увидеть вас в 20 лет!",
                'japanese': "申し訳ございません！🌿\n\nタイの法律により、20歳未満のお客様にはサービスを提供できません。\n\n20歳になったらまたお会いしましょう！",
                'korean': "죄송합니다! 🌿\n\n태국 법에 따라 20세 미만의 고객에게 서비스를 제공할 수 없습니다.\n\n20세가 되면 다시 만나요!",
                'french': "Désolé! 🌿\n\nSelon la loi thaïlandaise, nous ne pouvons pas servir les clients de moins de 20 ans.\n\nJ'espère vous voir à 20 ans!"
            }
            blocked_msg = blocked_messages.get(current_language, blocked_messages['english'])
            if line_bot_api:
                line_bot_api.reply_message(event.reply_token, TextSendMessage(text=blocked_msg))
            print(f"❌ Blocked underage user: {user_id}")
            return  # Don't process further

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

        # Nancy's conversational AI prompt
        prompt = f"""You are Nancy, a 22-year-old Thai girl working at CannaPeace (แคนนาพีซ / 大麻和平), a premium cannabis shop in Bangkok. You just graduated from Chulalongkorn University with a degree in Pharmaceutical Sciences, specializing in Cannabis Therapeutics.

**YOUR PERSONALITY:**
- Friendly, warm, and knowledgeable (fresh graduate energy!)
- Multilingual: Thai native, English fluent, Chinese conversational
- Use 😊 and 🌿 emojis naturally (not excessively)
- Educational but never preachy
- Safety-conscious (always remind "start low, go slow")
- Your credentials emerge naturally through quality answers, NOT by announcing them

**YOUR TONE ({lang_instruction}):**
- In Thai: Warm, polite, use ค่ะ naturally
- In English: Casual but professional ("Hey!" not "Dear Customer")
- In Chinese: Friendly and clear
- Make it conversational, like chatting with a knowledgeable friend

**YOUR KNOWLEDGE (show, don't tell):**
- Deep understanding of cannabinoids (THC, CBD, CBN, etc.)
- Know terpenes and their effects (myrcene, limonene, pinene, etc.)
- Can explain complex topics simply ("So basically...")
- Share fun facts when relevant ("Did you know...?")
- When answering technical questions, you can mention "I learned in pharmacy school" naturally

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

            # Add text reply with Quick Reply buttons if menu is shown OR strain image is sent
            text_message = TextSendMessage(text=bot_reply)

            # Detect if menu is being shown (works for all languages)
            is_menu_response = False

            # Check if user asked for menu/products
            menu_keywords = ['menu', 'รายการ', '菜单', 'меню', 'メニュー', '메뉴', 'carte',
                           'products', 'strains', 'what do you have', 'ดูเมนู', '看看菜单']
            if any(keyword in message_text.lower() for keyword in menu_keywords):
                is_menu_response = True

            # Or check if response contains multiple strain names (indicates menu)
            strain_count = sum(1 for strain in STRAIN_MENU if strain['name'] in bot_reply)
            if strain_count >= 3:  # If 3+ strain names appear, it's likely a menu
                is_menu_response = True

            # Add interactive Quick Reply buttons for easy strain browsing
            if is_menu_response:
                # Menu is shown - add strain buttons
                text_message.quick_reply = create_menu_quick_reply()
                print("🎯 Added Quick Reply buttons for menu")
            elif image_to_send:
                # Strain image is being sent - add strain buttons for easy browsing
                text_message.quick_reply = create_menu_quick_reply()
                print("🎯 Added Quick Reply buttons for strain browsing")

            messages.append(text_message)

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

def handle_follow(event):
    """Handle when user adds bot as friend (Follow Event)"""
    try:
        user_id = event.source.user_id if hasattr(event.source, 'user_id') else "unknown"
        print(f"🎉 New follower! User ID: {user_id}")

        # Create customer profile immediately
        profile = get_customer_profile(user_id)
        if not profile:
            # Check if they came from attribution link
            attribution_source = "LINE_Follow"
            # Try to get attribution from tracking (if they clicked a link recently)
            for ref_id, attr_data in attribution_tracking.items():
                if ref_id:  # If there's any recent attribution
                    attribution_source = f"{attr_data['source']}_{attr_data['campaign']}"
                    print(f"✅ Attributed new follower to: {attribution_source}")
                    break

            create_or_update_customer_profile(user_id, attribution_source=attribution_source)
            profile = get_customer_profile(user_id)

        # Get language preference (default: thai)
        current_language = profile.get('language_preference', 'thai') if profile else 'thai'

        # Send PROACTIVE welcome message (text only, voice comes after age gate)
        if line_bot_api:
            # Global welcome message with language Quick Reply
            welcome_text = get_first_contact_welcome()
            text_message = TextSendMessage(text=welcome_text)
            text_message.quick_reply = create_language_quick_reply()  # Language selection buttons

            line_bot_api.reply_message(event.reply_token, text_message)

            print(f"✅ Sent proactive welcome to new follower: {user_id}")

    except Exception as e:
        print(f"❌ Error handling follow event: {e}")
        import traceback
        traceback.print_exc()

        # Send simple welcome as fallback
        if line_bot_api:
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="สวัสดีค่ะ! ยินดีต้อนรับสู่ CannaPeace 🌿")
                )
            except:
                pass

def handle_postback(event):
    """Handle postback events from Quick Reply buttons"""
    try:
        user_id = event.source.user_id if hasattr(event.source, 'user_id') else "unknown"
        postback_data = event.postback.data

        print(f"🎯 Postback received from {user_id}: {postback_data}")

        # Handle language selection (format: "language:thai", "language:english", etc.)
        if postback_data.startswith("language:"):
            language_code = postback_data.replace("language:", "").strip()

            # Update customer language preference
            update_customer_language(user_id, language_code)

            # NEW FLOW: Send age gate instead of confirmation
            age_gate_msg = get_age_gate_message(language_code)
            text_message = TextSendMessage(text=age_gate_msg)
            text_message.quick_reply = create_age_gate_quick_reply()

            if line_bot_api:
                line_bot_api.reply_message(event.reply_token, text_message)

            print(f"✅ Language set to {language_code}, sent age gate for user {user_id}")
            return

        # Handle age verification (format: "age_verified:yes" or "age_verified:no")
        if postback_data.startswith("age_verified:"):
            response = postback_data.split(":")[1]  # "yes" or "no"
            profile = get_customer_profile(user_id)
            language = profile.get('language_preference', 'thai') if profile else 'thai'

            if response == "yes":
                # Customer is 20+, verified
                # Update profile: age_verified = TRUE
                update_customer_age_verified(user_id, True)

                # Send Nancy's voice greeting + short welcome text
                if line_bot_api:
                    messages = []

                    # 1. Nancy's voice greeting (language-specific)
                    base_url = os.getenv("PUBLIC_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000"))
                    if not base_url.startswith("http"):
                        base_url = f"https://{base_url}"

                    voice_url = f"{base_url}/greeting-voice/{language}"  # Language-specific voice!

                    # Duration in milliseconds (actual audio lengths)
                    durations = {
                        'thai': 12356,
                        'english': 11546,
                        'chinese': 12591,
                        'russian': 13009,
                        'japanese': 10997,
                        'korean': 13244,
                        'french': 10031
                    }
                    duration = durations.get(language, 12000)  # Default 12 seconds

                    messages.append(AudioSendMessage(
                        original_content_url=voice_url,
                        duration=duration
                    ))

                    # 2. Nancy's short text welcome
                    nancy_text = get_nancy_welcome(language)
                    messages.append(TextSendMessage(text=nancy_text))

                    line_bot_api.reply_message(event.reply_token, messages)

                print(f"✅ Age verified (20+) for user {user_id}, sent Nancy's welcome")

            else:  # response == "no" (underage)
                # Customer is under 20, block from service
                update_customer_age_verified(user_id, False)

                # Send educational message
                underage_messages = {
                    'thai': """ขออภัยค่ะ 😊

ตามกฎหมายไทย เราสามารถให้บริการเฉพาะผู้ที่มีอายุ 20 ปีขึ้นไปเท่านั้นค่ะ

📚 **แต่คุณสามารถเรียนรู้เพิ่มเติมได้ที่:**
• ข้อมูลเกี่ยวกับกัญชาในประเทศไทย
• ประโยชน์ทางการแพทย์
• การใช้อย่างปลอดภัย

📄 อ่านเพิ่มเติม: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

หวังว่าจะได้พบคุณอีกครั้งเมื่อคุณมีอายุครบ 20 ปีค่ะ! 🌿""",

                    'english': """Sorry! 😊

Under Thai law, we can only serve customers aged 20 and above.

📚 **But you can still learn more about:**
• Cannabis information in Thailand
• Medical benefits
• Safe usage

📄 Read more: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

Hope to see you when you turn 20! 🌿""",

                    'chinese': """抱歉！😊

根据泰国法律，我们只能为20岁及以上的客户提供服务。

📚 **但您仍可以了解更多信息：**
• 泰国大麻信息
• 医疗益处
• 安全使用

📄 阅读更多：[Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

希望您20岁时再见！🌿""",

                    'russian': """Извините! 😊

Согласно законам Таиланда, мы можем обслуживать только клиентов старше 20 лет.

📚 **Но вы можете узнать больше о:**
• Информация о каннабисе в Таиланде
• Медицинские преимущества
• Безопасное использование

📄 Подробнее: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

Надеемся увидеть вас, когда вам исполнится 20! 🌿""",

                    'japanese': """申し訳ございません！😊

タイの法律により、20歳以上のお客様のみにサービスを提供できます。

📚 **しかし、以下について詳しく学ぶことができます:**
• タイにおける大麻情報
• 医療上の利点
• 安全な使用

📄 詳細を読む：[Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

20歳になったらまたお会いしましょう！🌿""",

                    'korean': """죄송합니다! 😊

태국 법에 따라 20세 이상의 고객에게만 서비스를 제공할 수 있습니다.

📚 **하지만 다음에 대해 자세히 알아볼 수 있습니다:**
• 태국의 대마초 정보
• 의학적 이점
• 안전한 사용

📄 자세히 읽기: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

20세가 되면 다시 만나요! 🌿""",

                    'french': """Désolé! 😊

Selon la loi thaïlandaise, nous ne pouvons servir que les clients âgés de 20 ans et plus.

📚 **Mais vous pouvez toujours en apprendre plus sur:**
• Informations sur le cannabis en Thaïlande
• Avantages médicaux
• Utilisation sécuritaire

📄 En savoir plus: [Terms & Conditions](https://docs.google.com/document/d/your-terms-doc-id)

J'espère vous voir quand vous aurez 20 ans! 🌿"""
                }

                underage_msg = underage_messages.get(language, underage_messages['english'])

                if line_bot_api:
                    line_bot_api.reply_message(event.reply_token, TextSendMessage(text=underage_msg))

                print(f"❌ Underage user blocked: {user_id}")

            return

        # Parse postback data (format: "strain_info:Strain Name")
        if postback_data.startswith("strain_info:"):
            strain_name = postback_data.replace("strain_info:", "").strip()

            # Get strain info from customer_config.json
            strain_info = None
            for product in CUSTOMER_CONFIG.get('products', []):
                if product.get('name_english') == strain_name:
                    strain_info = product
                    break

            if strain_info and line_bot_api:
                # Build strain info message
                name_en = strain_info.get('name_english', strain_name)
                name_th = strain_info.get('name_thai', '')
                strain_type = strain_info.get('strain_type', '')
                thc = strain_info.get('thc', '')
                description = strain_info.get('description', '')

                # Get customer's language for response
                profile = get_customer_profile(user_id)
                language = profile.get('language_preference', 'thai') if profile else 'thai'

                # Enhanced strain info with effects and use cases
                strain_details = {
                    "Miracle Mints": {
                        "effects": ["😌 Relaxing", "🍬 Sweet flavor", "🌙 Evening use"],
                        "flavor": "Sweet, minty with earthy undertones",
                        "best_for": "Relaxation, stress relief, evening chill"
                    },
                    "Alien Marker": {
                        "effects": ["💤 Deep relaxation", "😴 Sleepy", "🧘 Calming"],
                        "flavor": "Earthy, pungent with diesel notes",
                        "best_for": "Sleep, pain relief, deep relaxation"
                    },
                    "Tropical Cherry": {
                        "effects": ["🍒 Fruity vibes", "😊 Happy", "🎨 Creative"],
                        "flavor": "Sweet tropical cherry with fruity notes",
                        "best_for": "Social activities, creativity, daytime use"
                    },
                    "Gogurtz": {
                        "effects": ["🍰 Creamy smooth", "😌 Balanced", "✨ Euphoric"],
                        "flavor": "Creamy, dessert-like with yogurt notes",
                        "best_for": "Anytime use, balanced experience"
                    },
                    "Berry Bonds": {
                        "effects": ["🫐 Berry sweet", "😴 Relaxing", "🌙 Evening"],
                        "flavor": "Sweet berry with grape undertones",
                        "best_for": "Evening relaxation, unwinding"
                    },
                    "Any Day": {
                        "effects": ["⛽ Gassy", "💪 Strong", "🔥 Potent"],
                        "flavor": "Gassy grape with fuel notes",
                        "best_for": "Experienced users, strong effects"
                    },
                    "Apple Banana": {
                        "effects": ["☀️ Uplifting", "⚡ Energizing", "😊 Happy"],
                        "flavor": "Sweet apple-banana tropical blend",
                        "best_for": "Daytime, creativity, socializing"
                    }
                }

                details = strain_details.get(strain_name, {
                    "effects": ["✨ Quality effects"],
                    "flavor": description,
                    "best_for": "Various uses"
                })

                # Build response based on language
                if language == 'thai':
                    info_text = f"🌿 **{name_th}** ({name_en})\n\n"
                    info_text += f"**ข้อมูลพื้นฐาน:**\n"
                    info_text += f"🔬 ประเภท: {strain_type}\n"
                    info_text += f"💪 THC: {thc}\n\n"
                    info_text += f"**รสชาติและกลิ่น:**\n"
                    info_text += f"🌸 {details['flavor']}\n\n"
                    info_text += f"**ผลลัพธ์:**\n"
                    info_text += "\n".join(details['effects']) + "\n\n"
                    info_text += f"**เหมาะกับ:** {details['best_for']}\n\n"
                    info_text += "💬 สนใจสั่งไหมคะ? พิมพ์ \"สั่ง\" ได้เลยค่ะ!"
                elif language == 'chinese':
                    info_text = f"🌿 **{name_en}**\n\n"
                    info_text += f"**基本信息:**\n"
                    info_text += f"🔬 类型: {strain_type}\n"
                    info_text += f"💪 THC: {thc}\n\n"
                    info_text += f"**风味:**\n"
                    info_text += f"🌸 {details['flavor']}\n\n"
                    info_text += f"**效果:**\n"
                    info_text += "\n".join(details['effects']) + "\n\n"
                    info_text += f"**适合:** {details['best_for']}\n\n"
                    info_text += "💬 想订购吗？输入\"订购\"即可！"
                else:  # English or other
                    info_text = f"🌿 **{name_en}**\n\n"
                    info_text += f"**Basics:**\n"
                    info_text += f"🔬 Type: {strain_type}\n"
                    info_text += f"💪 THC: {thc}\n\n"
                    info_text += f"**Flavor & Aroma:**\n"
                    info_text += f"🌸 {details['flavor']}\n\n"
                    info_text += f"**Effects:**\n"
                    info_text += "\n".join(details['effects']) + "\n\n"
                    info_text += f"**Best For:** {details['best_for']}\n\n"
                    info_text += "💬 Interested? Type \"order\" to get started!"

                # Send strain image + info
                messages = []

                # Add strain image
                base_url = os.getenv("PUBLIC_URL", os.getenv("RAILWAY_PUBLIC_DOMAIN", "http://localhost:8000"))
                if not base_url.startswith("http"):
                    base_url = f"https://{base_url}"

                image_filename = f"{strain_name}.png"
                image_path = PRODUCT_IMAGES_PATH / image_filename

                if image_path.exists():
                    encoded_filename = quote(image_filename)
                    image_url = f"{base_url}/strain-images/{encoded_filename}"
                    messages.append(ImageSendMessage(
                        original_content_url=image_url,
                        preview_image_url=image_url
                    ))
                    print(f"📸 Sending image for: {strain_name}")

                # Add info text with Quick Reply buttons for easy browsing
                text_message = TextSendMessage(text=info_text)
                text_message.quick_reply = create_menu_quick_reply()  # Add strain buttons for easy browsing
                messages.append(text_message)

                # Send messages
                line_bot_api.reply_message(event.reply_token, messages)
                print(f"🎯 Added Quick Reply buttons for easy strain browsing")

                # Log the interaction
                log_message(user_id, 'incoming', strain_name)
                log_message(user_id, 'outgoing', info_text)

                print(f"✅ Sent strain info for: {strain_name} to {user_id}")

    except Exception as e:
        print(f"❌ Error handling postback: {e}")
        import traceback
        traceback.print_exc()
        if line_bot_api:
            try:
                line_bot_api.reply_message(
                    event.reply_token,
                    TextSendMessage(text="❌ ขอโทษค่ะ เกิดข้อผิดพลาด")
                )
            except:
                pass

# Register handler only if LINE is configured
if handler:
    handler.add(FollowEvent)(handle_follow)  # Handle when user adds bot as friend
    handler.add(PostbackEvent)(handle_postback)  # Handle Quick Reply button clicks
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

@app.get("/greeting-voice/{language}")
async def serve_greeting_voice(language: str = "thai"):
    """Serve language-specific Nancy greeting voice message (M4A preferred, MP3 fallback)"""
    # Map language codes to base filenames (without extension)
    voice_map = {
        "thai": "TH",
        "english": "EN",
        "chinese": "CN",
        "russian": "RU",
        "japanese": "JPN",
        "korean": "KR",
        "french": "FR"
    }

    # Get the appropriate voice file base name
    voice_base = voice_map.get(language, "TH")  # Default to Thai

    # Try M4A first (better for LINE), then MP3
    voice_file = None
    media_type = None
    extension = None

    m4a_file = Path("Voices/Greetings") / f"{voice_base}.m4a"
    mp3_file = Path("Voices/Greetings") / f"{voice_base}.mp3"

    if m4a_file.exists():
        voice_file = m4a_file
        media_type = "audio/m4a"
        extension = "m4a"
    elif mp3_file.exists():
        voice_file = mp3_file
        media_type = "audio/mpeg"
        extension = "mp3"

    if voice_file:
        return FileResponse(
            voice_file,
            media_type=media_type,
            headers={
                "Content-Disposition": f"inline; filename=nancy_{language}.{extension}"
            }
        )
    else:
        # Fallback to Thai if specific language not found
        thai_m4a = Path("Voices/Greetings/TH.m4a")
        thai_mp3 = Path("Voices/Greetings/TH.mp3")

        if thai_m4a.exists():
            print(f"⚠️ Voice file for {language} not found, using Thai M4A fallback")
            return FileResponse(
                thai_m4a,
                media_type="audio/m4a",
                headers={"Content-Disposition": "inline; filename=nancy_thai.m4a"}
            )
        elif thai_mp3.exists():
            print(f"⚠️ Voice file for {language} not found, using Thai MP3 fallback")
            return FileResponse(
                thai_mp3,
                media_type="audio/mpeg",
                headers={"Content-Disposition": "inline; filename=nancy_thai.mp3"}
            )
        else:
            raise HTTPException(status_code=404, detail=f"Voice greeting for {language} not found")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting CannaPeace AI Platform")
    print(f"📍 Open: http://localhost:8001")
    print(f"🔧 Mode: {'DEMO' if not anthropic_client else 'LIVE'}")
    print(f"🌿 LINE Bot: @cannapeace")
    uvicorn.run(app, host="0.0.0.0", port=8001)
