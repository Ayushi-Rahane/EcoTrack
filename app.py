from flask import Flask, render_template, request, redirect, url_for, session, flash
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

@app.route('/')
def dashboard():
    if not session.get('logged_in') or not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('index.html')



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE email = %s AND password_hash = %s"
        cursor.execute(query, (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['logged_in'] = True
            session['user_id'] = user['User_ID']
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))



@app.route('/vendor_login', methods=['GET', 'POST'])
def vendor_login():
    if request.method == 'POST':
        email = request.form['username']
        password = request.form['password']

        cursor = db.cursor(dictionary=True)
        query = "SELECT * FROM vendors WHERE contact_email = %s AND password_hash = %s"
        cursor.execute(query, (email, password))
        vendor = cursor.fetchone()
        cursor.close()

        if vendor:
            session['logged_in'] = True
            session['vendor_id'] = vendor['Vendor_ID']
            return redirect(url_for('vendor_dashboard'))
        else:
            return render_template('vendor_login.html', error="Invalid credentials")
    return render_template('vendor_login.html')


@app.route('/vendor_logout')
def vendor_logout():
    session.clear()
    return redirect(url_for('vendor_login'))



@app.route('/vendor_dashboard')
def vendor_dashboard():
    vendor_id = session.get('vendor_id')
    if not vendor_id:
        return redirect(url_for('vendor_login'))

    cursor = db.cursor(dictionary=True)

    # Fetch vendor details
    cursor.execute("SELECT * FROM Vendors WHERE Vendor_ID = %s", (vendor_id,))
    vendor = cursor.fetchone()

    # Fetch recent reports
    cursor.execute("SELECT * FROM Plastic_Waste WHERE Vendor_ID = %s ORDER BY Report_Date DESC LIMIT 5", (vendor_id,))
    recent_reports = cursor.fetchall()

    cursor.close()

    return render_template('vendor_dashboard.html', vendor=vendor, recent_reports=recent_reports)



from datetime import date as dt_date

@app.route('/add_waste', methods=['POST'])
def add_waste():
    if not session.get('vendor_id'):
        return redirect(url_for('vendor_login'))

    vendor_id = session['vendor_id']
    date_value = request.form['date'] or dt_date.today().strftime("%Y-%m-%d")  # default to today
    total_waste = request.form['total_waste']
    category = request.form['category']
    notes = request.form['notes']

    cursor = db.cursor()
    cursor.execute("""
        INSERT INTO Plastic_Waste (Vendor_ID, Report_Date, Total_Waste_kg, Waste_Category, Notes)
        VALUES (%s, %s, %s, %s, %s)
    """, (vendor_id, date_value, total_waste, category, notes))
    db.commit()
    cursor.close()

    flash("Waste report submitted successfully!", "success")
    return redirect(url_for('vendor_dashboard'))

@app.route('/add_vendor', methods=['GET', 'POST'])
def add_vendor():
    if not session.get('user_id'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        vendor_name = request.form['vendor_name']
        vendor_type = request.form['vendor_type']
        location = request.form['location']
        contact_name = request.form['contact_name']
        contact_email = request.form['contact_email']
        phone_number = request.form['contact_phone']
        password = request.form['contact_password']  # vendor login password

        cursor = db.cursor()
        query = """INSERT INTO vendors 
                   (vendor_name, vendor_type, location, contact_name, contact_phone, contact_email, password_hash, registered_by) 
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
        cursor.execute(query, (vendor_name, vendor_type, location, contact_name, phone_number, contact_email, password, session['user_id']))
        db.commit()
        cursor.close()

        flash("Vendor added successfully!", "success")
        return redirect(url_for('add_vendor'))

    return render_template('add_vendor.html')


if __name__ == '__main__':
    app.run(debug=True)
