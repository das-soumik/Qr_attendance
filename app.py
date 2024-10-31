from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
import qrcode
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Directory to save QR codes
QR_FOLDER = 'static/qrcodes'
if not os.path.exists(QR_FOLDER):
    os.makedirs(QR_FOLDER)

# Home route to scan QR code
@app.route('/')
def index():
    return render_template('index.html')

# Route to generate QR codes for each user
@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    if request.method == 'POST':
        user_id = request.form['user_id']
        name = request.form['name']
        
        # Insert into database
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
            conn.commit()
            
            # Generate QR code
            qr_data = f"http://localhost:5000/attendance/{user_id}"
            img = qrcode.make(qr_data)
            img.save(f"{QR_FOLDER}/{user_id}.png")
            
            flash("QR code generated successfully!", "success")
        except sqlite3.IntegrityError:
            flash("User ID already exists.", "danger")
        
        conn.close()
        
    return render_template('generate_qr.html')

# Route to log attendance when QR code is scanned
@app.route('/attendance/<user_id>')
def attendance(user_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Check if user exists
    c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
    user = c.fetchone()
    if user:
        # Log attendance
        c.execute("INSERT INTO attendance_logs (user_id) VALUES (?)", (user_id,))
        conn.commit()
        message = f"Attendance recorded for {user[1]}"
    else:
        message = "User not found"
    
    conn.close()
    return render_template('attendance.html', message=message)

# Route to view attendance logs
@app.route('/view_attendance')
def view_attendance():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    # Query to get the user names and attendance timestamps
    c.execute("""
        SELECT users.name, attendance_logs.timestamp 
        FROM attendance_logs 
        JOIN users ON users.user_id = attendance_logs.user_id
        ORDER BY attendance_logs.timestamp DESC
    """)
    logs = c.fetchall()  # Fetch all attendance records
    conn.close()
    return render_template('attendance_log.html', logs=logs)

