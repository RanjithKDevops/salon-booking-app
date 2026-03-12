from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3
from datetime import datetime, timedelta
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Database initialization
def init_db():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS bookings
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  customer_name TEXT NOT NULL,
                  customer_email TEXT NOT NULL,
                  customer_phone TEXT NOT NULL,
                  service TEXT NOT NULL,
                  booking_date DATE NOT NULL,
                  booking_time TIME NOT NULL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Initialize DB when app starts
init_db()

# Services offered
SERVICES = [
    'Haircut - €25',
    'Hair Coloring - €60',
    'Manicure - €30',
    'Pedicure - €35',
    'Facial - €45'
]

# Time slots
TIME_SLOTS = ['09:00', '10:00', '11:00', '12:00', '14:00', '15:00', '16:00', '17:00']

@app.route('/')
def index():
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings ORDER BY booking_date, booking_time")
    bookings = c.fetchall()
    conn.close()
    return render_template('index.html', services=SERVICES, bookings=bookings)

@app.route('/book', methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        service = request.form['service']
        date = request.form['date']
        time = request.form['time']
        
        # Input validation
        if not all([name, email, phone, service, date, time]):
            flash('All fields are required!', 'error')
            return redirect(url_for('book'))
        
        if '@' not in email or '.' not in email:
            flash('Invalid email address!', 'error')
            return redirect(url_for('book'))
        
        # Check if slot is available
        conn = sqlite3.connect('bookings.db')
        c = conn.cursor()
        c.execute("SELECT * FROM bookings WHERE booking_date = ? AND booking_time = ?", 
                 (date, time))
        if c.fetchone():
            flash('This time slot is already booked!', 'error')
            conn.close()
            return redirect(url_for('book'))
        
        # Save booking
        c.execute("""INSERT INTO bookings 
                     (customer_name, customer_email, customer_phone, service, booking_date, booking_time) 
                     VALUES (?, ?, ?, ?, ?, ?)""",
                 (name, email, phone, service, date, time))
        conn.commit()
        conn.close()
        
        flash('Booking successful!', 'success')
        return redirect(url_for('index'))
    
    # Generate available dates (next 7 days)
    dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    return render_template('book.html', services=SERVICES, time_slots=TIME_SLOTS, dates=dates)

@app.route('/delete/<int:booking_id>')
def delete_booking(booking_id):
    conn = sqlite3.connect('bookings.db')
    c = conn.cursor()
    c.execute("DELETE FROM bookings WHERE id = ?", (booking_id,))
    conn.commit()
    conn.close()
    flash('Booking deleted successfully!', 'success')
    return redirect(url_for('index'))

@app.route('/health')
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
