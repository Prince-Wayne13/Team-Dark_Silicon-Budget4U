import os
import json
import re
import firebase_admin
from firebase_admin import credentials, db, firestore
from dotenv import load_dotenv

# Import your custom parser
# Ensure aiparser.py is in the same directory or Python path
from aiparser import llama3_openrouter_parser

# Load environment variables (API keys, etc.)
load_dotenv()

# --- CONFIGURATION ---
DATA_FOLDER = r"D:\Backup folder\Code\GitHub\trial"
SERVICE_ACCOUNT_PATH = r"D:\Backup folder\Code\GitHub\trial\serviceAccountKey.json"
DATABASE_URL = 'https://trial-31bb9-default-rtdb.firebaseio.com/'
MAX_SMS_TO_PROCESS = 25

# --- FIREBASE INITIALIZATION ---
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred, {
        'databaseURL': DATABASE_URL
    })

db_fs = firestore.client()

def is_real_transaction(sender, message):
    """Filters SMS to ensure only financial transactions are processed."""
    if not message:
        return False

    msg_lower = message.lower()
    sender_lower = str(sender).lower()

    # Filter out marketing/system spam
    promo_keywords = ["congratulations", "spin & win", "bonus", "promo", "free", "valid until", "internet settings"]
    if any(p in msg_lower for p in promo_keywords) or sender_lower == "airtel":
        return False

    # Identify transaction markers
    transaction_keywords = [
        "received mk", "sent mk", "paid mk", "withdrawn mk", 
        "credited", "debited", "bal:", "cash in", "cash out"
    ]

    id_patterns = [
        r"Ref[:\s]+[A-Z0-9]+",
        r"Trans ID[:\s]+[A-Z0-9\.]+",
        r"Approval Code[:\s]+\d+",
        r"[A-Z]{2}\d{6,}"  
    ]

    has_keyword = any(k in msg_lower for k in transaction_keywords)
    has_id = any(re.search(p, message, re.IGNORECASE) for p in id_patterns)

    return has_keyword or has_id

def process_user_transactions(uid):
    """Loads, filters, parses, and uploads transactions for a specific UID."""
    file_path = os.path.join(DATA_FOLDER, f"{uid}_messages.json")
    
    if not os.path.exists(file_path):
        print(f"File not found for user: {uid}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        messages = json.load(f)

    # Filter exactly 25 real transaction messages
    filtered_sms = {}
    count = 0
    for sms in messages:
        if count >= MAX_SMS_TO_PROCESS: 
            break 
        sender = sms.get("sender", "")
        msg = sms.get("message", "")
        
        if is_real_transaction(sender, msg):
            filtered_sms[f"sms_{count}"] = {"sender": sender, "message": msg}
            count += 1

    if not filtered_sms:
        print(f"No valid transactions found for {uid}")
        return

    try:
        # AI Parsing
        parsed_transactions = llama3_openrouter_parser(filtered_sms, uid)
        
        if isinstance(parsed_transactions, list):
            history_ref = db_fs.collection('Transactions').document(uid).collection('history')

            for item in parsed_transactions:
                amt = float(item.get('amount') or 0)
                fee = float(item.get('fees') or 0)
                
                clean_entry = {
                    "Source": item.get('source'),
                    "Direction": item.get('direction'),
                    "Type": item.get('type'),
                    "Amount": amt + fee,
                    "Date": item.get('timestamp'),
                    "Reference": item.get('reference'),
                    "Counterparty": item.get('counterparty'),
                    "Currency": item.get('currency', 'MWK'),
                    "Description": item.get('description', 'Parsed Transaction'),
                    "SyncedAt": firestore.SERVER_TIMESTAMP
                }

                # Use Reference as Doc ID to prevent duplicates
                ref_id = item.get('reference')
                if ref_id:
                    safe_id = re.sub(r'[./\s]', '_', str(ref_id))
                    history_ref.document(safe_id).set(clean_entry, merge=True)
                else:
                    history_ref.add(clean_entry)
            
            print(f"✅ Sync complete: {len(parsed_transactions)} items added for {uid}")

    except Exception as e:
        print(f"❌ Error processing {uid}: {e}")

def main():
    """Main execution point: Fetches UIDs from RTDB and starts processing."""
    print("Starting Sync Process...")
    
    # Get UIDs from Realtime Database
    users_ref = db.reference('user_sms').get()
    
    if not users_ref:
        print("No users found in Realtime Database.")
        return

    uids = users_ref.keys()
    print(f"Found {len(uids)} users. Beginning processing...\n")

    for uid in uids:
        print(f"Processing UID: {uid}...")
        process_user_transactions(uid)

if __name__ == '__main__':
    main()