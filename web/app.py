from flask import Flask, render_template, jsonify
import firebase_admin
from firebase_admin import credentials, db

app= Flask(__name__)

#firebase setup
cred = credentials.Certificate('########')
firebase_admin.initialize_app(cred, {
    'databaseURL': '#########'     
})

@app.route('/')
def dashboard():
    return render_template('dashboard.html')




@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


@app.route('/budget')
def budget():
    return render_template('budget.html')

@app.route('/records')
def records():
    return render_template('records.html')


if __name__ == '__main__':
    app.run(debug=True)