#!/usr/bin/env python3
"""
CRM Google Sheets Setup Script
================================
Sets up the Google Sheets structure for v2.0 CRM implementation.

This script:
1. Renames Sheet1 to "Orders" (if needed)
2. Adds new columns to Orders sheet
3. Creates 4 new sheets: Customers, Messages, Journey_Events, Attribution_Links
4. Adds proper headers to all sheets

Run once to initialize the CRM structure.
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import base64

# Get credentials
GOOGLE_SHEET_ID = "1Rz1DbllW-0ezJKM4Qsf58D8WAMPxuP5HOXzAbVgMQIY"
GOOGLE_CREDENTIALS_BASE64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")
GOOGLE_CREDENTIALS_PATH = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")

def get_sheets_service():
    """Initialize Google Sheets API service"""
    # Try base64-encoded credentials first
    if GOOGLE_CREDENTIALS_BASE64:
        creds_json = base64.b64decode(GOOGLE_CREDENTIALS_BASE64).decode('utf-8')
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=credentials)

    # Fall back to file path
    from pathlib import Path
    if Path(GOOGLE_CREDENTIALS_PATH).exists():
        credentials = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_PATH,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=credentials)

    raise Exception("No Google credentials found. Set GOOGLE_CREDENTIALS_BASE64 or GOOGLE_CREDENTIALS_PATH")

def get_sheet_info(service):
    """Get current sheet structure"""
    sheet_metadata = service.spreadsheets().get(spreadsheetId=GOOGLE_SHEET_ID).execute()
    sheets = sheet_metadata.get('sheets', [])
    return sheets

def rename_sheet(service, sheet_id, new_title):
    """Rename a sheet"""
    request = {
        'requests': [{
            'updateSheetProperties': {
                'properties': {
                    'sheetId': sheet_id,
                    'title': new_title
                },
                'fields': 'title'
            }
        }]
    }
    service.spreadsheets().batchUpdate(
        spreadsheetId=GOOGLE_SHEET_ID,
        body=request
    ).execute()
    print(f"✅ Renamed sheet to '{new_title}'")

def create_sheet(service, title):
    """Create a new sheet"""
    request = {
        'requests': [{
            'addSheet': {
                'properties': {
                    'title': title
                }
            }
        }]
    }
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=GOOGLE_SHEET_ID,
        body=request
    ).execute()
    print(f"✅ Created sheet '{title}'")
    return response

def add_headers(service, sheet_name, headers):
    """Add headers to a sheet"""
    body = {'values': [headers]}
    service.spreadsheets().values().update(
        spreadsheetId=GOOGLE_SHEET_ID,
        range=f'{sheet_name}!A1',
        valueInputOption='USER_ENTERED',
        body=body
    ).execute()
    print(f"✅ Added {len(headers)} headers to '{sheet_name}'")

def setup_crm_structure():
    """Main setup function"""
    print("🚀 Setting up CRM Google Sheets structure...")
    print(f"📊 Sheet ID: {GOOGLE_SHEET_ID}")

    service = get_sheets_service()

    # 1. Get current sheets
    print("\n1️⃣ Checking current sheets...")
    sheets = get_sheet_info(service)
    sheet_titles = {sheet['properties']['title']: sheet['properties']['sheetId'] for sheet in sheets}
    print(f"   Found sheets: {list(sheet_titles.keys())}")

    # 2. Rename Sheet1 to Orders (if it exists)
    if 'Sheet1' in sheet_titles and 'Orders' not in sheet_titles:
        print("\n2️⃣ Renaming Sheet1 to Orders...")
        rename_sheet(service, sheet_titles['Sheet1'], 'Orders')
        sheet_titles['Orders'] = sheet_titles.pop('Sheet1')
    else:
        print("\n2️⃣ Orders sheet already exists or Sheet1 not found")

    # 3. Update Orders sheet headers (v2.0 structure)
    print("\n3️⃣ Setting up Orders sheet headers...")
    orders_headers = [
        'Timestamp',
        'LINE_User_ID',
        'Name',
        'Phone',
        'Items',
        'Total',
        'Address',
        'Status',
        'Attribution_Source'
    ]

    # Check if Orders sheet has data
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Orders!A1:I1'
        ).execute()
        existing_headers = result.get('values', [[]])[0]

        if len(existing_headers) < len(orders_headers):
            # Add headers (this will replace existing)
            add_headers(service, 'Orders', orders_headers)
        else:
            print(f"   Orders sheet already has {len(existing_headers)} columns")
    except:
        # No data yet, add headers
        add_headers(service, 'Orders', orders_headers)

    # 4. Create Customers sheet
    print("\n4️⃣ Setting up Customers sheet...")
    if 'Customers' not in sheet_titles:
        create_sheet(service, 'Customers')

    customers_headers = [
        'LINE_User_ID',
        'Phone',
        'Name',
        'First_Seen',
        'Last_Seen',
        'Total_Orders',
        'Lifetime_Value',
        'Acquisition_Source',
        'Current_Journey_Stage',
        'Segment',
        'Favorite_Strains',
        'Tags'
    ]
    add_headers(service, 'Customers', customers_headers)

    # 5. Create Messages sheet
    print("\n5️⃣ Setting up Messages sheet...")
    if 'Messages' not in sheet_titles:
        create_sheet(service, 'Messages')

    messages_headers = [
        'Timestamp',
        'LINE_User_ID',
        'Direction',
        'Content',
        'Detected_Intent',
        'Journey_Stage_Before',
        'Journey_Stage_After'
    ]
    add_headers(service, 'Messages', messages_headers)

    # 6. Create Journey_Events sheet
    print("\n6️⃣ Setting up Journey_Events sheet...")
    if 'Journey_Events' not in sheet_titles:
        create_sheet(service, 'Journey_Events')

    journey_headers = [
        'Event_ID',
        'LINE_User_ID',
        'Event_Type',
        'From_Stage',
        'To_Stage',
        'Timestamp',
        'Metadata'
    ]
    add_headers(service, 'Journey_Events', journey_headers)

    # 7. Create Attribution_Links sheet
    print("\n7️⃣ Setting up Attribution_Links sheet...")
    if 'Attribution_Links' not in sheet_titles:
        create_sheet(service, 'Attribution_Links')

    attribution_headers = [
        'Link_ID',
        'Channel',
        'UTM_Campaign',
        'UTM_Medium',
        'UTM_Source',
        'Total_Clicks',
        'Total_Conversions',
        'Revenue',
        'Created_Date'
    ]
    add_headers(service, 'Attribution_Links', attribution_headers)

    print("\n✅ CRM Google Sheets structure setup complete!")
    print("\n📋 Summary:")
    print("   - Orders: 9 columns (added LINE_User_ID, Status, Attribution_Source)")
    print("   - Customers: 12 columns (new sheet)")
    print("   - Messages: 7 columns (new sheet)")
    print("   - Journey_Events: 7 columns (new sheet)")
    print("   - Attribution_Links: 9 columns (new sheet)")
    print(f"\n🔗 View sheet: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit")

if __name__ == "__main__":
    try:
        setup_crm_structure()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
