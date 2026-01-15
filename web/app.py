from flask import Flask, render_template, jsonify
import firebase_admin
from firebase_admin import credentials, db

app= Flask(__name__)
'''#firebase setup
cred = credentials.Certificate('########')
firebase_admin.initialize_app(cred, {
    'databaseURL': '#########'     
})'''


@app.route('/')
def index():
    return render_template('index.html')




@app.route('/boxes')
def boxes():
    return render_template('boxes.html')


@app.route('/transactions')
def transactions():
    return render_template('transactions.html')




if __name__ == '__main__':
    app.run(debug=True)