from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb.cursors
import re
import hashlib
import re
import requests

app = Flask(__name__)
CORS(app)  # Enable requests from React frontend

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'vuln_guard'

mysql = MySQL(app)

def hash_password(password):
    """Hash password for simple demonstration."""
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    name = data.get('name', '')
    email = data.get('email', '')
    password = data.get('password', '')

    if not (name and email and password):
        return jsonify({'error': 'Please fill in all fields'}), 400
    if len(password) < 8:
        return jsonify({'error': 'Password must be at least 8 characters long'}), 400
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        return jsonify({'error': 'Invalid email address'}), 400

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
    user = cursor.fetchone()
    if user:
        return jsonify({'error': 'Account already exists!'}), 409

    hashed_pw = hash_password(password)
    cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', (name, email, hashed_pw))
    mysql.connection.commit()
    return jsonify({'message': 'You have successfully registered!'}), 201

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')

    if not (email and password):
        return jsonify({'error': 'Please fill in all fields'}), 400

    hashed_pw = hash_password(password)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, hashed_pw))
    user = cursor.fetchone()
    if user:
        return jsonify({'message': 'Logged in successfully!', 'user': {'email': user['email'], 'name': user['name']}}), 200
    else:
        return jsonify({'error': 'Incorrect email/password!'}), 401
    
@app.route('/api/add_repository', methods=['POST'])
def add_repository():
    data = request.json
    repo_url = data.get('repoUrl', '').strip()

    if not repo_url:
        return jsonify({'error': 'Repository URL is required'}), 400

    # Regex validation (as before)
    github_regex = r'^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/?$'
    match = re.match(github_regex, repo_url)
    if not match:
        return jsonify({'error': 'Invalid GitHub repository URL'}), 400

    # Extract owner and repo for API check
    owner, repo = match.group(1), match.group(2)
    api_url = f"https://api.github.com/repos/{owner}/{repo}"
    resp = requests.get(api_url, timeout=5)
    if resp.status_code != 200:
        return jsonify({'error': 'Repository does not exist or is private'}), 400

    # ... your DB/store logic here ...
    return jsonify({'message': 'Repository added successfully!'}), 201





if __name__ == '__main__':
    app.run(debug=True)
