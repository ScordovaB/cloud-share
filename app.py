from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for


app = Flask(__name__, static_url_path='/static')

# Configure MySQL connection
app.config['MYSQL_DATABASE_HOST'] = 'your_rds_endpoint'
app.config['MYSQL_DATABASE_USER'] = 'your_database_username'
app.config['MYSQL_DATABASE_PASSWORD'] = 'your_database_password'
app.config['MYSQL_DATABASE_DB'] = 'your_database_name'

mysql = MySQL(app)

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Connect to MySQL database
    conn = mysql.connect()
    cursor = conn.cursor()

    # Execute query to check user credentials
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cursor.fetchone()

    if user:
        return redirect(url_for('dashboard'))
    else:
        return "Invalid username or password. Please try again."

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Connect to MySQL database
        conn = mysql.connect()
        cursor = conn.cursor()

        # Execute query to insert new user
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
        conn.commit()

        return redirect(url_for('dashboard'))
    else:
        return render_template('create_user.html')

if __name__ == '__main__':
    app.run(debug=True)
