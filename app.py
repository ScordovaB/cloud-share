from flask import Flask, render_template, request, redirect, url_for, session, flash
import pymysql.cursors
from flask_bcrypt import Bcrypt
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__, static_url_path='/static')
bcrypt = Bcrypt(app)

# Flask app configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['MYSQL_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE_DB')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_DATABASE_PORT', 3306))
app.secret_key = os.getenv('SECRET_KEY')

# Database connection function
def get_db_connection():
    return pymysql.connect(host=app.config['MYSQL_HOST'],
                           user=app.config['MYSQL_USER'],
                           password=app.config['MYSQL_PASSWORD'],
                           db=app.config['MYSQL_DB'],
                           port=app.config['MYSQL_PORT'],
                           charset='utf8mb4',
                           cursorclass=pymysql.cursors.DictCursor)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username=%s", (username,))
            user = cursor.fetchone()

            if user and bcrypt.check_password_hash(user['password'], password):
                session['user_id'] = user['user_id']  # Adjusted to use dictionary access
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid username or password. Please try again.")
                return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/upload')
def upload():
    return render_template('upload.html', session = session)

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, username, hashed_password))
                conn.commit()
                flash("User created successfully. Please log in.")
                return redirect(url_for('index'))

    return render_template('create_user.html')

if __name__ == '__main__':
    app.run(debug=True)
