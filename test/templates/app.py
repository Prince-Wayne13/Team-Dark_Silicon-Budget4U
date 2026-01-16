from flask import Flask, render_template, jsonify, request, session
import firebase_admin
from firebase_admin import credentials, firestore, db # Added db for RTDB access
import os

app = Flask(__name__)
app.secret_key = "YOUR_SUPER_SECRET_KEY" # REQUIRED for session to work

# 1. Setup the specific Clean Database project
if not firebase_admin._apps:
    cred = credentials.Certificate(r"D:\Backup folder\Code\GitHub\trial\budget4Udb.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://trial-31bb9-default-rtdb.firebaseio.com/' # Required for RTDB
    })

# Use consistent naming for your handles
db_fs = firestore.client()
# rtdb = db.reference() # Uncomment if you need direct RTDB access

# --- PAGE ROUTES ---

@app.route('/')
def index():
    return render_template('index.html')

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
    # add
    
    return "Settings Page Coming Soon"

@app.route('/help')
def help():
    #add
    return "Help and FAQ Page" 

# --- DATABASE API ROUTES ---

# 1. GET ALL TRANSACTIONS
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    # Hardcoding the UID for testing
    uid = "2CNOtZiKmHNsDDgkbcVhLbHAjxS2" 
    
    try:
        # Fetching from your specific Firestore path
        docs = db_fs.collection('Transactions').document(uid).collection('TransIDs').order_by('Date', direction='DESCENDING')
        docs = docs.stream()
        history = []
        for doc in docs:
            data = doc.to_dict()
            
            # Mapping your specific database fields to what JS expects
            transaction = {
                "id": doc.id,
                "amount": data.get('Amount', 0),
                "fromTo": data.get('Source', 'N/A'), # Using Source as 'fromTo'
                "description": data.get('Reference', 'N/A'),
                "direction": data.get('Direction', 'N/A'), # Using Reference as desc
                "date": data.get('Date', 'N/A')
            }
            history.append(transaction)
            
        return jsonify(history)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. CREATE NEW TRANSACTION

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    # Hardcoded UID for testing
    uid = "2CNOtZiKmHNsDDgkbcVhLbHAjxS2" 
    data = request.json
    
    try:
        # 1. Reference to the user's transaction history
        history_ref = db_fs.collection('Transactions').document(uid).collection('TransIDs')
        
        # 2. Add the new document
        new_doc_ref = history_ref.document()
        new_doc_ref.set({
            'Date': data.get('Date'),
            'Source': data.get('Source'),
            'Reference': data.get('Reference'),
            'Amount': float(data.get('Amount', 0)),
            'Direction': data.get('Direction', 'Inbound'),
            'timestamp': firestore.SERVER_TIMESTAMP # Helps with sorting by newest
        })
        
        return jsonify({"success": True, "id": new_doc_ref.id})

    except Exception as e:
        print(f"Firestore Error: {e}")
        return jsonify({"error": "Failed to connect to Firestore. Check your connection."}), 500
    
# 3. DELETE TRANSACTION
@app.route('/api/transactions/delete', methods=['POST'])
def delete_transaction():
    uid = "2CNOtZiKmHNsDDgkbcVhLbHAjxS2" 
    
    data = request.json
    trans_id = data.get('transID') 
    
    try:
        # Path: Transactions -> {uid} -> history -> {trans_id}
        db_fs.collection('Transactions').document(uid).collection('TransIDs').document(trans_id).delete()
        return jsonify({"success": True})
    except Exception as e:
        print(f"Delete Error: {e}")
        return jsonify({"error": str(e)}), 400
    

# 4. UPDATE TRANSACTION
@app.route('/api/transactions/update', methods=['POST'])
def update_transaction():
    uid = session.get('user_id')
    if not uid: return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    trans_id = data.get('id')
    
    try:
        doc_ref = db_fs.collection('Transactions').document(uid).collection('TransIDs').document(trans_id)
        doc_ref.update({
            'description': data.get('edit-description'),
            'amount': float(data.get('edit-amount', 0))
        })
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"error": str(e)}), 400



@app.route('/api/stats', methods=['GET'])
def get_stats():
    uid = "2CNOtZiKmHNsDDgkbcVhLbHAjxS2"
    try:
        docs = db_fs.collection('Transactions').document(uid).collection('TransIDs').stream()
        
        total_income = 0
        total_expenditure = 0
        
        for doc in docs:
            data = doc.to_dict()
            amount = float(data.get('Amount', 0))
            # Clean the string to handle any accidental spaces
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





















if __name__ == '__main__':
    app.run(debug=True)