import firebase_admin
from firebase_admin import credentials, auth, db, firestore
import requests
from flask import Flask, request, session, render_template, redirect, url_for, jsonify
from datetime import datetime

# --- FLASK APP SETUP ---
app = Flask(__name__)
app.secret_key = "YOUR_SUPER_SECRET_FLASK_KEY"

# --- INITIALIZATION messy---
cred = credentials.Certificate(r"D:\Backup folder\Code\GitHub\Team-Dark_Silicon-Budget4U\test\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://trial-31bb9-default-rtdb.firebaseio.com/'
})

# --- 2. INITIALIZE CLEAN DB (FIRESTORE) ---
cred_clean = credentials.Certificate(r"D:\Backup folder\Code\GitHub\Team-Dark_Silicon-Budget4U\wayne\budget4Udb.json")
clean_project_app = firebase_admin.initialize_app(cred_clean, name="clean_project")

db_fs = firestore.client()  
rtdb_root = db.reference()  
db_fs_clean = firestore.client(app=clean_project_app)
FIREBASE_WEB_API_KEY = "AIzaSyB0Ty2tiRNQq0hZNPnYBYhbM7VmBUouFtM" 

# --- FLASK ROUTES ---  
@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    
    try:
        user = auth.create_user(email=email, password=password)
        db.reference(f'users/{user.uid}').set({
            'email': email,
            'balance': 0,
        })
        
        send_email_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        id_token = get_user_id_token(email, password)
        
        email_payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        }
        requests.post(send_email_url, json=email_payload)
        return "Verification email sent! Please check your inbox.", 200

    except Exception as e:
        return str(e), 400

def get_user_id_token(email, password):
    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(login_url, json=data)
    return res.json().get('idToken')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {
        "email": email, 
        "password": password, 
        "returnSecureToken": True
    }
    
    try:
        response = requests.post(auth_url, json=payload)
        data = response.json()

        if response.status_code == 200:
            user_id = data['localId']
            user_record = auth.get_user(user_id)
            if not user_record.email_verified:
                return "Email not verified. Please check your inbox!", 403
            
            try:
                user_ref = db_fs.collection('Transactions').document(user_id)
                user_ref.set({
                    'last_sync': firestore.SERVER_TIMESTAMP,
                    'status': 'active',
                    'email': email
                }, merge=True)
                session['user_id'] = user_id
            except Exception as sync_error:
                print(f"Firestore Sync Warning: {sync_error}")

            session['user_id'] = user_id
            return redirect(url_for('dashboard'))
        else:
            error_message = data.get('error', {}).get('message', 'Invalid Credentials')
            return f"Login failed: {error_message}", 401

    except Exception as e:
        return f"An internal error occurred: {str(e)}", 500
    
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    try:
        user_record = auth.get_user(user_id)
        if not user_record.email_verified:
            session.pop('user_id', None)
            return render_template('login.html', error="Please verify your email before accessing the dashboard.")

        user_data = db.reference(f'users/{user_id}').get()
        
        return render_template('index.html', user=user_data)
        
    except Exception as e:
        return redirect(url_for('login_page'))

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_page'))

@app.route('/boxes')
def boxes():
    return render_template('boxes.html')

@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

@app.route('/aichatbot')
def aichatbot():    
    return render_template('aichatbot.html')

@app.route('/settings')
def settings():
    return "Settings Page Coming Soon"

@app.route('/help')
def help():
    return "Help and FAQ Page" 

# --- DATABASE API ROUTES ---

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    try:
        docs = db_fs_clean.collection('Transactions').document(uid).collection('TransIDs').order_by('Date', direction='DESCENDING').stream()
        
        history = []
        for doc in docs:
            data = doc.to_dict()
            
            # Mapping your specific database fields to what JS expects
            transaction = {
                "id": doc.id,
                "amount": data.get('Amount', 0),
                "fromTo": data.get('Source', 'N/A'), # Using Source as 'fromTo'
                "description": data.get('Reference', 'N/A'), # Using Reference as desc
                'Direction': data.get('Direction', 'Inbound'),
                "date": data.get('Date', 'N/A')
            }
            history.append(transaction)
            
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        history_ref = db_fs_clean.collection('Transactions').document(uid).collection('TransIDs')
        new_doc_ref = history_ref.document()
        
        # We Map the JS keys (left) to your Firestore fields (right)
        new_doc_ref.set({
            'Date': data.get('date'),
            'Source': data.get('fromTo'),
            'Reference': data.get('description'),
            'Amount': float(data.get('amount', 0)),
            'Direction': data.get('direction').upper(), # Save as INBOUND/OUTBOUND
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        source_name = data.get('fromTo') # This MUST match the Box Name
        amount = float(data.get('amount'))
        direction = data.get('direction') # 'INCOMING' or 'OUTGOING'

        # 1. Save the transaction (existing code...)
        
        # 2. Update the Box Balance
        # Find the box where the name matches the transaction source
        boxes_ref = db_fs.collection('Boxes').document(uid).collection('UserBoxes')
        query = boxes_ref.where('name', '==', source_name).limit(1).get()

        if query:
            box_doc = query[0]
            current_val = float(box_doc.to_dict().get('total_value', 0))
            
            # Calculate new balance
            new_val = current_val + amount if direction == 'INCOMING' else current_val - amount
            
            # Update the box in Firestore
            boxes_ref.document(box_doc.id).update({'total_value': new_val})
        return jsonify({"success": True})
    
    except Exception as e:
             return jsonify({"error": str(e)}), 500
    
@app.route('/api/transactions/delete', methods=['POST'])
def delete_transaction():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    trans_id = data.get('transID') 
    
    try:
        db_fs_clean.collection('Transactions').document(uid).collection('TransIDs').document(trans_id).delete()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/transactions/update', methods=['POST'])
def update_transaction():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    trans_id = data.get('id')
    
    try:
        doc_ref = db_fs_clean.collection('Transactions').document(uid).collection('TransIDs').document(trans_id)
        doc_ref.update({
            'description': data.get('edit-description'),
            'amount': float(data.get('edit-amount', 0))
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    try:
        docs = db_fs_clean.collection('Transactions').document(uid).collection('TransIDs').stream()
        total_income = 0
        total_expenditure = 0
        
        for doc in docs:
            data = doc.to_dict()
            amount = float(data.get('Amount', 0))
            direction = str(data.get('Direction', '')).strip().upper()
            
            if direction == "INCOMING":
                total_income += amount
            elif direction == "OUTGOING":
                total_expenditure += amount
                
        return jsonify({
            "income": total_income,
            "expenditure": total_expenditure
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

@app.route('/api/boxes', methods=['GET'])
def get_boxes():
    uid = session.get('user_id')
    if not uid: return jsonify([]), 401

    # Exact paths from your database
    boxes_ref = db_fs_clean.collection('Boxes').document(uid).collection('UserBoxes')
    trans_ref = db_fs_clean.collection('Transactions').document(uid).collection('TransIDs')
    
    boxes = []
    try:
        # Load all transactions into memory once
        all_transactions = [t.to_dict() for t in trans_ref.stream()]

        for doc in boxes_ref.stream():
            box = doc.to_dict()
            box['id'] = doc.id
            
            # Normalize box name for matching: "Shop Rent" -> "shop rent"
            box_name_clean = box.get('name', '').lower().strip()
            manual_bal = float(box.get('manual_balance', 0))

            income_in = 0
            income_out = 0
            
            for t_data in all_transactions:
                # Using Title Case 'Source' as per your snippet
                t_source = str(t_data.get('Source', '')).lower().strip()
                
                if t_source == box_name_clean:
                    # Using Title Case 'Amount'
                    amt = float(t_data.get('Amount', 0))
                    
                    # Using Title Case 'Direction'
                    # We compare lowercase 'incoming' to the lowercase version of the data
                    t_dir = str(t_data.get('Direction', '')).lower().strip()
                    
                    if t_dir == "incoming":
                        income_in += amt
                    elif t_dir == "outgoing":
                        income_out += amt

            # The Net Balance Calculation
            current_balance = (manual_bal + income_in) - income_out
            
            box['income_in'] = income_in
            box['income_out'] = income_out
            box['total_value'] = current_balance
            boxes.append(box)

        return jsonify(boxes)
    except Exception as e:
        print(f"Logic Error: {e}")
        return jsonify({"error": str(e)}), 500

    except Exception as e:
        print(f"Error in get_boxes: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/boxes', methods=['POST'])
def create_box():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        box_ref = db_fs_clean.collection('Boxes').document(uid).collection('UserBoxes').document()
        
        box_ref.set({
            'name': data.get('name'),
            'category': data.get('category'), # e.g., Revenue, Expense
            'description': data.get('description', ''),
            'total_value': float(data.get('initial_balance', 0)),
            'budget_goal': float(data.get('budget_goal', 0)),
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return jsonify({"success": True, "id": box_ref.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/boxes/<box_id>', methods=['PUT'])
def update_box(box_id):
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        # Update Firestore
        box_ref = db_fs.collection('Boxes').document(uid).collection('UserBoxes').document(box_id)
        box_ref.update({
            'name': data.get('name'),
            'budget_goal': float(data.get('budget_goal', 0)),
            'manual_balance': float(data.get('manual_balance', 0))
        })
        return jsonify({"success": True}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/api/boxes/<box_id>', methods=['DELETE'])
def delete_box(box_id):
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    try:
        db_fs_clean.collection('Boxes').document(uid).collection('UserBoxes').document(box_id).delete()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 500








if __name__ == '__main__':
    app.run(debug=True)