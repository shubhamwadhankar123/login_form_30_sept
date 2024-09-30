from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Ideally, store this in environment variables

# MySQL Connection Configuration
def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Shubhamw@1234",  # Keep this secure in a production environment
        database="user_auth"
    )

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        db = get_db_connection()
        cursor = db.cursor()

        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, hashed_password))
            db.commit()
            flash('You have registered successfully', 'success')
            return redirect(url_for('login'))
        except mysql.connector.IntegrityError:
            flash('Username already exists', 'danger')
            return redirect(url_for('register'))
        finally:
            cursor.close()
            db.close()

    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        db = get_db_connection()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        cursor.close()
        db.close()

        if user and check_password_hash(user['password'], password):
            session['username'] = user['username']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard')
def dashboard():
    if 'username' in session:
        return f"Welcome, {session['username']}!"
    return redirect(url_for('login'))

# Logout Route
@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out', 'info')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
