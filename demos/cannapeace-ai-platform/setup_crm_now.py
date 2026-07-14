#!/usr/bin/env python3
"""
Immediate CRM Sheets Setup - Run this now!
==========================================
This script will create all 5 CRM sheets in your Google Sheet right now.
Uses Railway environment variables automatically.
"""

from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import json
import base64

# Configuration
GOOGLE_SHEET_ID = "1Rz1DbllW-0ezJKM4Qsf58D8WAMPxuP5HOXzAbVgMQIY"

def get_sheets_service():
    """Initialize Google Sheets API service"""
    # Try Railway environment variable
    creds_base64 = os.getenv("GOOGLE_CREDENTIALS_BASE64")

    if creds_base64:
        print("✅ Found GOOGLE_CREDENTIALS_BASE64 environment variable")
        creds_json = base64.b64decode(creds_base64).decode('utf-8')
        creds_dict = json.loads(creds_json)
        credentials = service_account.Credentials.from_service_account_info(
            creds_dict,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=credentials)

    # Try local credentials file
    from pathlib import Path
    creds_path = os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json")
    if Path(creds_path).exists():
        print(f"✅ Found credentials file: {creds_path}")
        credentials = service_account.Credentials.from_service_account_file(
            creds_path,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        return build('sheets', 'v4', credentials=credentials)

    raise Exception(
        "❌ No Google credentials found!\n"
        "Set GOOGLE_CREDENTIALS_BASE64 environment variable or provide credentials.json"
    )

def main():
    print("=" * 70)
    print("CannaPeace CRM Sheets Setup")
    print("=" * 70)
    print(f"\n📊 Google Sheet ID: {GOOGLE_SHEET_ID}")
    print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit\n")

    # Initialize service
    print("1️⃣ Connecting to Google Sheets API...")
    try:
        service = get_sheets_service()
        print("   ✅ Connected successfully!\n")
    except Exception as e:
        print(f"   ❌ Failed: {e}")
        return 1

    # Get current sheets
    print("2️⃣ Checking current sheet structure...")
    try:
        sheet_metadata = service.spreadsheets().get(spreadsheetId=GOOGLE_SHEET_ID).execute()
        sheets = sheet_metadata.get('sheets', [])
        sheet_titles = {s['properties']['title']: s['properties']['sheetId'] for s in sheets}
        print(f"   Current sheets: {list(sheet_titles.keys())}\n")
    except Exception as e:
        print(f"   ❌ Failed to read sheet: {e}")
        return 1

    # Define CRM structure
    crm_sheets = {
        'Orders': [
            'Timestamp', 'LINE_User_ID', 'Name', 'Phone', 'Items',
            'Total', 'Address', 'Status', 'Attribution_Source'
        ],
        'Customers': [
            'LINE_User_ID', 'Phone', 'Name', 'First_Seen', 'Last_Seen',
            'Total_Orders', 'Lifetime_Value', 'Acquisition_Source',
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
    print("3️⃣ Renaming Sheet1 to Orders (if needed)...")
    if 'Sheet1' in sheet_titles and 'Orders' not in sheet_titles:
        try:
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
            service.spreadsheets().batchUpdate(
                spreadsheetId=GOOGLE_SHEET_ID, body=request
            ).execute()
            print("   ✅ Renamed Sheet1 → Orders")
            sheet_titles['Orders'] = sheet_titles.pop('Sheet1')
        except Exception as e:
            print(f"   ⚠️ Could not rename: {e}")
    else:
        print("   ℹ️ Orders sheet already exists or Sheet1 not found")

    # Create missing sheets
    print("\n4️⃣ Creating missing CRM sheets...")
    sheets_created = []
    for sheet_name, headers in crm_sheets.items():
        if sheet_name not in sheet_titles:
            try:
                # Create sheet
                request = {
                    'requests': [{
                        'addSheet': {
                            'properties': {'title': sheet_name}
                        }
                    }]
                }
                service.spreadsheets().batchUpdate(
                    spreadsheetId=GOOGLE_SHEET_ID, body=request
                ).execute()
                print(f"   ✅ Created sheet: {sheet_name}")

                # Add headers
                body = {'values': [headers]}
                service.spreadsheets().values().update(
                    spreadsheetId=GOOGLE_SHEET_ID,
                    range=f'{sheet_name}!A1',
                    valueInputOption='USER_ENTERED',
                    body=body
                ).execute()
                print(f"      ➕ Added {len(headers)} headers")
                sheets_created.append(sheet_name)

            except Exception as e:
                print(f"   ❌ Failed to create {sheet_name}: {e}")
        else:
            print(f"   ℹ️ {sheet_name} already exists")

    # Update Orders sheet headers if needed
    print("\n5️⃣ Updating Orders sheet headers...")
    try:
        result = service.spreadsheets().values().get(
            spreadsheetId=GOOGLE_SHEET_ID,
            range='Orders!A1:I1'
        ).execute()
        existing_headers = result.get('values', [[]])[0] if result.get('values') else []

        if len(existing_headers) < 9:
            body = {'values': [crm_sheets['Orders']]}
            service.spreadsheets().values().update(
                spreadsheetId=GOOGLE_SHEET_ID,
                range='Orders!A1',
                valueInputOption='USER_ENTERED',
                body=body
            ).execute()
            print(f"   ✅ Updated Orders headers ({len(existing_headers)} → 9 columns)")
        else:
            print(f"   ℹ️ Orders already has {len(existing_headers)} columns")
    except Exception as e:
        print(f"   ⚠️ Could not update Orders headers: {e}")

    # Final verification
    print("\n6️⃣ Verifying final structure...")
    try:
        sheet_metadata = service.spreadsheets().get(spreadsheetId=GOOGLE_SHEET_ID).execute()
        final_sheets = [s['properties']['title'] for s in sheet_metadata.get('sheets', [])]
        print(f"   Final sheets: {final_sheets}")
    except Exception as e:
        print(f"   ⚠️ Could not verify: {e}")

    # Summary
    print("\n" + "=" * 70)
    print("✅ CRM SHEETS SETUP COMPLETE!")
    print("=" * 70)
    if sheets_created:
        print(f"\n📝 Sheets created: {', '.join(sheets_created)}")
    else:
        print("\n📝 All sheets already existed (no new sheets created)")

    print(f"\n🔗 View your sheet: https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit")
    print("\n🎯 Next: Test the LINE bot to see CRM in action!")
    print("   - Send a message → Customer profile created")
    print("   - Place an order → Order + profile updated")
    print("   - Check Messages sheet → Conversation logged")

    return 0

if __name__ == "__main__":
    try:
        exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️ Cancelled by user")
        exit(1)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
