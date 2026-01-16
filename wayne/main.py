import firebase_admin
from firebase_admin import credentials, auth, db, firestore
import requests
from flask import Flask, request, session, render_template, redirect, url_for, jsonify
from datetime import timedelta

# --- FLASK APP SETUP ---
app = Flask(__name__)
app.secret_key = "YOUR_SUPER_SECRET_FLASK_KEY"
app.permanent_session_lifetime = timedelta(days=7)

# --- FIREBASE INITIALIZATION ---
# Default App (For Auth and RTDB)
cred = credentials.Certificate(r"D:\Backup folder\Code\GitHub\Team-Dark_Silicon-Budget4U\test\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://trial-31bb9-default-rtdb.firebaseio.com/'
})

# Clean Project App (For Firestore Transactions)
cred_clean = credentials.Certificate(r"D:\Backup folder\Code\GitHub\Team-Dark_Silicon-Budget4U\wayne\budget4Udb.json")
clean_project_app = firebase_admin.initialize_app(cred_clean, name="clean_project")

# Handles
db_fs_clean = firestore.client(app=clean_project_app)
FIREBASE_WEB_API_KEY = "AIzaSyB0Ty2tiRNQq0hZNPnYBYhbM7VmBUouFtM" 

# --- HELPERS ---
def get_user_id_token(email, password):
    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(login_url, json=data)
    return res.json().get('idToken')

# --- FLASK ROUTES (Auth & Pages) ---

@app.route('/')
def login_page():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup_page')
def signup_page():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup():
    email = request.form.get('email')
    password = request.form.get('password')
    try:
        # 1. Create the user in Firebase Auth
        user = auth.create_user(email=email, password=password)
        
        # 2. Create their budget folder in RTDB
        db.reference(f'users/{user.uid}').set({
            'email': email,
            'balance': 0,
        })
        
        # 3. Trigger verification email
        send_email_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        id_token = get_user_id_token(email, password)
        email_payload = {"requestType": "VERIFY_EMAIL", "idToken": id_token}
        requests.post(send_email_url, json=email_payload)

        return "Verification email sent! Please check your inbox.", 200
    except Exception as e:
        return str(e), 400

@app.route('/login', methods=['POST'])
def login():
    session.clear()
    email = request.form.get('email')
    password = request.form.get('password')
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    
    try:
        response = requests.post(auth_url, json={"email": email, "password": password, "returnSecureToken": True})
        data = response.json()

        if response.status_code == 200:
            user_id = data['localId']
            user_record = auth.get_user(user_id)
            
            # Check Verification
            if not user_record.email_verified:
                return "Email not verified. Please check your inbox!", 403
            
            # SYNC STEP: Ensure Firestore folder is active
            try:
                user_ref = db_fs_clean.collection('Transactions').document(user_id)
                user_ref.set({
                    'last_sync': firestore.SERVER_TIMESTAMP,
                    'status': 'active',
                    'email': email
                }, merge=True)
                print(f"Successfully synced UID {user_id} to Firestore.")
            except Exception as sync_error:
                print(f"Firestore Sync Warning: {sync_error}")

            # Establish Session
            session.permanent = True
            session['user_id'] = user_id
            
            # Return JSON for JS redirect or use standard redirect
            if request.is_json or request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({"status": "success", "redirect": url_for('dashboard')}), 200
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
            return render_template('login.html', error="Please verify email.")

        user_data = db.reference(f'users/{user_id}').get()
        return render_template('index.html', user=user_data)
    except:
        return redirect(url_for('login_page'))

@app.route('/transactions')
def transactions():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    return render_template('transactions.html')

@app.route('/boxes')
def boxes():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    return render_template('boxes.html')

@app.route('/ai-advisor')
def aichatbot():
    if 'user_id' not in session: return redirect(url_for('login_page'))
    return render_template('aichatbot.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_page'))

# --- API ROUTES ---

@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    uid = session.get('user_id')
    if not uid: return jsonify([])
    
    docs = db_fs_clean.collection('Transactions').document(uid).collection('history').order_by('timestamp', direction='DESCENDING').stream()
    return jsonify([{**doc.to_dict(), "id": doc.id} for doc in docs])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        amt = float(data.get('Amount', 0))
        direction = data.get('Direction', 'Outbound') 

        # 1. Clean Firestore History
        db_fs_clean.collection('Transactions').document(uid).collection('history').add({
            'Amount': amt,
            'Source': data.get('Source', 'N/A'),
            'Date': data.get('Date', 'N/A'),
            'Reference': data.get('Reference', 'N/A'),
            'Direction': direction,
            'timestamp': firestore.SERVER_TIMESTAMP
        })
        
        # 2. Update Balance in RTDB
        user_ref = db.reference(f'users/{uid}')
        current_bal = user_ref.get().get('balance', 0)
        new_bal = (current_bal + amt) if direction == 'Inbound' else (current_bal - amt)
        user_ref.update({'balance': new_bal})
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/stats', methods=['GET'])
def get_stats():
    uid = session.get('user_id')
    if not uid: return jsonify({"income": 0, "expenditure": 0})
    
    docs = db_fs_clean.collection('Transactions').document(uid).collection('history').stream()
    inc, exp = 0, 0
    for doc in docs:
        d = doc.to_dict()
        amt = float(d.get('Amount', 0))
        if d.get('Direction') == 'Inbound': inc += amt
        else: exp += amt
    return jsonify({"income": inc, "expenditure": exp})

if __name__ == '__main__':
    app.run(debug=True)