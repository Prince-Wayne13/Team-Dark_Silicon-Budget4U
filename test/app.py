import firebase_admin
from firebase_admin import credentials, auth, db
import requests
from flask import Flask, request, session, render_template, redirect, url_for

app = Flask(__name__)
app.secret_key = "YOUR_SUPER_SECRET_FLASK_KEY"

# 1. Initialize Firebase Admin SDK
cred = credentials.Certificate(r"D:\Backup folder\Code\GitHub\Team-Dark_Silicon-Budget4U\test\serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://trial-31bb9-default-rtdb.firebaseio.com/'
})

# 2. Web API Key for Auth
FIREBASE_WEB_API_KEY = "AIzaSyB0Ty2tiRNQq0hZNPnYBYhbM7VmBUouFtM" 

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
    
    # Verify credentials via REST API
    auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_WEB_API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    
    response = requests.post(auth_url, json=payload)
    data = response.json()

    if response.status_code == 200:
        user_id = data['localId']
        
        # Check verification status BEFORE allowing the session to start
        user_record = auth.get_user(user_id)
        if not user_record.email_verified:
            return "Email not verified. Please check your inbox!", 403
            
        session['user_id'] = user_id
        return "Success", 200
    else:
        return "Invalid Email or Password", 401

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

if __name__ == '__main__':
    app.run(debug=True)