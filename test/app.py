import firebase_admin
from firebase_admin import credentials, auth, db, firestore
import requests
from flask import Flask, request, session, render_template, redirect, url_for, jsonify



# --- FLASK APP SETUP ---
app = Flask(__name__)
app.secret_key = "YOUR_SUPER_SECRET_FLASK_KEY"

# --- INITIALIZATION ---
cred = credentials.Certificate(r"D:\Backup folder\Code\GitHub\Team-Dark_Silicon-Budget4U\test\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://trial-31bb9-default-rtdb.firebaseio.com/'
})


db_fs = firestore.client()  
rtdb_root = db.reference()  
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
        # 1. Create the user in Firebase
        user = auth.create_user(email=email, password=password)
        
        # 2. Create their budget folder in the database
        db.reference(f'users/{user.uid}').set({
            'email': email,
            'balance': 0,
        })
        
        
        # 3. Trigger the verification email
        # We use the REST API to send the actual email to the user's inbox
        send_email_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={FIREBASE_WEB_API_KEY}"
        
        # We need an ID token to tell Firebase WHICH user to send the email to
        id_token = get_user_id_token(email, password)
        
        email_payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        }
        requests.post(send_email_url, json=email_payload)

        # IMPORTANT: We do NOT set session['user_id'] here. 
        # This keeps them locked out of the dashboard.
        
        return "Verification email sent! Please check your inbox.", 200

    except Exception as e:
        return str(e), 400

# Helper function to get the token for the email trigger
def get_user_id_token(email, password):
    login_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    data = {"email": email, "password": password, "returnSecureToken": True}
    res = requests.post(login_url, json=data)
    return res.json().get('idToken')

@app.route('/login', methods=['POST'])
def login():
    email = request.form.get('email')
    password = request.form.get('password')
    
    # 1. Verify credentials via Google Identity REST API
    # (Since Firebase Admin SDK doesn't handle password verification directly)
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
            
            # 2. Check if the user has verified their email
            user_record = auth.get_user(user_id)
            if not user_record.email_verified:
                return "Email not verified. Please check your inbox!", 403
            
            # 3. THE SYNC STEP (Integrated from your second script)
            # This ensures the Firestore document exists/is updated upon login
            try:
                # We use 'db_fs' to match your Transaction API handles
                user_ref = db_fs.collection('Transactions').document(user_id)
                
                # Write to Firestore to ensure the user "folder" is active
                user_ref.set({
                    'last_sync': firestore.SERVER_TIMESTAMP,
                    'status': 'active',
                    'email': email
                }, merge=True)
                
                print(f"Successfully synced UID {user_id} to Firestore.")
            except Exception as sync_error:
                # We log the error but allow login to continue 
                # so the user isn't locked out by a database sync glitch
                print(f"Firestore Sync Warning: {sync_error}")

            # 4. Establish the Flask Session
            session['user_id'] = user_id
            return "Success", 200

        else:
            # Handle incorrect password or user not found
            error_message = data.get('error', {}).get('message', 'Invalid Credentials')
            return f"Login failed: {error_message}", 401

    except Exception as e:
        return f"An internal error occurred: {str(e)}", 500
    
@app.route('/dashboard')
def dashboard():
    # 1. Check if they are even logged into the Flask session
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    user_id = session['user_id']
    
    try:
        # 2. Fetch the REAL-TIME status from Firebase Auth
        user_record = auth.get_user(user_id)
        
        # 3. THE LOCK: If not verified, destroy session and redirect
        if not user_record.email_verified:
            session.pop('user_id', None) # Log them out
            return render_template('login.html', error="Please verify your email before accessing the dashboard.")

        # 4. Only if verified, fetch data and show index.html
        user_data = db.reference(f'users/{user_id}').get()
        return render_template('index.html', user=user_data)
        
    except Exception as e:
        return redirect(url_for('login_page'))
    

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login_page'))



# --- DATABASE API ROUTES  ---

# CREATE & UPDATE
@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    # 1. Add to Firestore History
    doc_ref = db_fs.collection('Transactions').document(uid).collection('history').document()
    doc_ref.set({
        'item': data['item'],
        'amount': float(data['amount']),
        'timestamp': firestore.SERVER_TIMESTAMP
    })
    
    # 2. Update RTDB Balance
    user_ref = db.reference(f'users/{uid}')
    balance = user_ref.get().get('balance', 0) - float(data['amount'])
    user_ref.update({'balance': balance})
    
    return jsonify({"success": True, "id": doc_ref.id})

# READ
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    uid = session.get('user_id')
    docs = db_fs.collection('Transactions').document(uid).collection('history').order_by('timestamp', direction='DESCENDING').stream()
    history = [{**doc.to_dict(), "id": doc.id} for doc in docs]
    return jsonify(history)

# DELETE
@app.route('/api/transactions/<doc_id>', methods=['DELETE'])
def delete_transaction(doc_id):
    uid = session.get('user_id')
    db_fs.collection('Transactions').document(uid).collection('history').document(doc_id).delete()
    return jsonify({"success": True})
if __name__ == '__main__':
    app.run(debug=True)