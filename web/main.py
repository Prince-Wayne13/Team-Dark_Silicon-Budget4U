import os
import json
import re
import firebase_admin
from firebase_admin import credentials, db
from flask import Flask, render_template, abort
from dotenv import load_dotenv
from aiparser import gemini_transaction_parser
import time


load_dotenv()
app = Flask(__name__)

DATA_FOLDER = r"D:\Backup folder\Code\GitHub\trial"

MAX_SMS = 30



# FIREBASE SETUP

if not firebase_admin._apps:
    cred = credentials.Certificate(
        r"D:\Backup folder\Code\GitHub\trial\serviceAccountKey.json"
    )
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://trial-31bb9-default-rtdb.firebaseio.com/'
    })




def is_real_transaction(sender, message):
    if not message:
        return False

    # 1. Clean data 
    msg_lower = message.lower()
    sender_lower = str(sender).lower()

    
    promo_keywords = ["congratulations", "spin & win", "bonus", "promo", "free", "valid until", "internet settings"]
    if any(p in msg_lower for p in promo_keywords) or sender_lower == "airtel":
        return False

    # 3. Financial Keywords
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

    # Return True only if it has financial intent AND a traceable ID/Balance
    return has_keyword or has_id

# ROUTES

@app.route('/')
def dashboard():
    users_ref = db.reference('user_sms').get()
    uids = users_ref.keys() if users_ref else []
    return render_template('dashboard.html', uids=uids)

@app.route('/user/<uid>')
def view_user(uid):
    file_path = os.path.join(DATA_FOLDER, f"{uid}_messages.json")

    if not os.path.exists(file_path):
        abort(404, description=f"{uid}_messages.json not found")

    # Load raw SMS data
    with open(file_path, 'r', encoding='utf-8') as f:
        raw_data = json.load(f)

    messages = raw_data if isinstance(raw_data, list) else list(raw_data.values())

    if not messages:
        abort(404, description="No messages found")

    
    # STEP 1: REGEX FILTERING
    
    filtered_sms = {}
    count = 0

    for idx, sms in enumerate(messages):
        if count >= MAX_SMS:
            break

        sender = sms.get("sender", "")
        message = sms.get("message", "")

        if is_real_transaction(sender, message):
            filtered_sms[f"sms_{count}"] = {
                "sender": sender,
                "message": message
            }
            count += 1

    print(f"Regex filtered {count} financial SMS (capped at {MAX_SMS})")

   #ai parsing
    parsed_transactions = []

    if filtered_sms:
        print(f"Parsing all {len(filtered_sms)}.")
        try:
            parsed_transactions = gemini_transaction_parser(filtered_sms, uid)
            if isinstance(parsed_transactions, list):
                print(f"AI parsing success ({len(parsed_transactions)} transactions)")
            else:
                parsed_transactions = []
                print(" AI returned no transactions")
        except Exception as e:
            parsed_transactions = []
            print(f" AI parsing failed: {e}")

    
    return render_template(
        "user_view.html",
        uid=uid,
        summary=json.dumps(parsed_transactions, indent=2),
        messages=messages
    )


# --------------------------------------------------
# MAIN
# --------------------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
