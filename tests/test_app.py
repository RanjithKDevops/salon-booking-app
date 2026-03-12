import pytest
import sqlite3
import os
from app import app, init_db

@pytest.fixture
def client():
    app.config['TESTING'] = True
    # Initialize test database
    if os.path.exists('test_bookings.db'):
        os.remove('test_bookings.db')
    
    # Override database connection for testing
    def get_test_db():
        conn = sqlite3.connect('test_bookings.db')
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
        return conn
    
    # Monkey patch the database connection
    import app as app_module
    app_module.sqlite3.connect = lambda db: get_test_db()
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    if os.path.exists('test_bookings.db'):
        os.remove('test_bookings.db')

def test_home_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert b'healthy' in response.data

def test_booking_page(client):
    response = client.get('/book')
    assert response.status_code == 200

def test_create_booking(client):
    response = client.post('/book', data={
        'name': 'Test User',
        'email': 'test@example.com',
        'phone': '1234567890',
        'service': 'Haircut - €25',
        'date': '2026-12-25',
        'time': '10:00'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Booking successful' in response.data
