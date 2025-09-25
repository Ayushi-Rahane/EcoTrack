from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector

app = Flask(__name__)
app.secret_key = 'f982769ef50cb351c6905ac625fdea35' 

# MySQL connection setup
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="imastronaut",
    database="ecotrack"
)
# Dashboard API
@app.route('/')
def dashboard():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return render_template('index.html')

#Login API
@app.route('/login', methods=['GET', 'POST'])
def login():
    if(request.method =='POST'):
        username = request.form['username']
        password = request.form['password'] 

        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        if user:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

# Logout api 
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))
 
if __name__ == '__main__':
    app.run(debug=True)