from flask import Flask, request, jsonify
import firebase_admin
from firebase_admin import credentials, auth, firestore
from functools import wraps

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

app = Flask(__name__)

def firebase_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header:
            return jsonify({"error": "Missing Authorization header"}), 401

        try:
            token = auth_header.split(" ")[1]
            decoded = auth.verify_id_token(token)
            request.uid = decoded["uid"]
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401

        return f(*args, **kwargs)
    return decorated

@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    if not email or not password or not username:
        return jsonify({"error": "Missing fields"}), 400

    try:
        user = auth.create_user(
            email=email,
            password=password
        )

        db.collection("users").document(user.uid).set({
            "username": username,
            "email": email,
            "createdAt": firestore.SERVER_TIMESTAMP
        })

        return jsonify({
            "message": "User created",
            "uid": user.uid
        }), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/transaction", methods=["POST"])
@firebase_required
def create_transaction():
    data = request.json
    tran_id = data.get("tranId")
    amount = data.get("amount")
    description = data.get("description", "")

    if not tran_id or amount is None:
        return jsonify({"error": "Missing transaction data"}), 400

    db.collection("users") \
      .document(request.uid) \
      .collection("transactions") \
      .document(tran_id) \
      .set({
          "amount": amount,
          "description": description,
          "status": "active",
          "last_sync": firestore.SERVER_TIMESTAMP
      })

    return jsonify({"message": "Transaction created"}), 201

@app.route("/transactions", methods=["GET"])
@firebase_required
def get_transactions():
    docs = db.collection("users") \
             .document(request.uid) \
             .collection("transactions") \
             .stream()

    transactions = []
    for doc in docs:
        t = doc.to_dict()
        t["tranId"] = doc.id
        transactions.append(t)

    return jsonify(transactions), 200

@app.route("/me", methods=["GET"])
@firebase_required
def get_profile():
    doc = db.collection("users").document(request.uid).get()

    if not doc.exists:
        return jsonify({"error": "User not found"}), 404

    return jsonify(doc.to_dict()), 200

if __name__ == "__main__":
    app.run(debug=True)
