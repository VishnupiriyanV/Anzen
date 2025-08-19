import os
import threading
from flask import Flask, request, jsonify, session
from flask_mysqldb import MySQL
from flask_cors import CORS
import MySQLdb.cursors
import hashlib
import re
import requests
import json
import subprocess
import urllib.parse
import shutil
from datetime import timedelta
from flask_session import Session

app = Flask(__name__)

from flask_cors import CORS

CORS(app, 
     supports_credentials=True,
     resources={
         r"/api/*": {
             "origins": ["http://localhost:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "expose_headers": ["Set-Cookie"],
             "max_age": 3600
         }
     })

app.config.update(
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'dev-fallback-key'),
    SESSION_COOKIE_SECURE=True,  # True in production
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=timedelta(hours=1)
)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'vuln_guard'

mysql = MySQL(app)

# Create database tables if they don't exist
with app.app_context():
    cursor = mysql.connection.cursor()
    
    # Create users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `users` (
          `id` INT(11) NOT NULL AUTO_INCREMENT,
          `name` VARCHAR(100) NOT NULL,
          `email` VARCHAR(100) NOT NULL UNIQUE,
          `password` VARCHAR(255) NOT NULL,
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    # Create repositories table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `repositories` (
          `id` INT(11) NOT NULL AUTO_INCREMENT,
          `user_id` INT(11) NOT NULL,
          `name` VARCHAR(255) NOT NULL,
          `url` VARCHAR(255) NOT NULL,
          `status` ENUM('pending', 'scanning', 'completed', 'error') NOT NULL DEFAULT 'pending',
          `last_scan` DATETIME DEFAULT NULL,
          `total_vulnerabilities` INT(11) DEFAULT 0,
          `high_vuln` INT(11) DEFAULT 0,
          `medium_vuln` INT(0) DEFAULT 0,
          `low_vuln` INT(11) DEFAULT 0,
          `score` INT(11) DEFAULT 0,
          PRIMARY KEY (`id`),
          UNIQUE KEY `user_repo_url` (`user_id`, `url`),
          FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)

    # Create vulnerabilities table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS `vulnerabilities` (
          `id` INT(11) NOT NULL AUTO_INCREMENT,
          `repo_id` INT(11) NOT NULL,
          `severity` VARCHAR(50) NOT NULL,
          `title` TEXT NOT NULL,
          `description` TEXT,
          `file` VARCHAR(255) NOT NULL,
          `line` INT(11) NOT NULL,
          `remediation` TEXT,
          `false_positive_analysis` TEXT,
          PRIMARY KEY (`id`),
          FOREIGN KEY (`repo_id`) REFERENCES `repositories` (`id`) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
    """)
    
    mysql.connection.commit()
    cursor.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def calculate_score(vuln_counts):
    """
    Calculates a simple security score based on vulnerability counts.
    """
    total_points = (vuln_counts['high'] * 10) + (vuln_counts['medium'] * 6) + (vuln_counts['low'] * 3)
    total_vulns = vuln_counts['high'] + vuln_counts['medium'] + vuln_counts['low']
    
    if total_vulns > 0:
        max_possible_points = total_vulns * 10
        score = int(100 - (total_points / max_possible_points) * 100)
    else:
        score = 100
        
    return score

def run_scan_pipeline(repo_url, user_id):
    """
    Runs the full scanning pipeline in a separate thread.
    """
    with app.app_context():
        repo_name = repo_url.split('/')[-1]
        repo_id = None
        # Ensure a new cursor is created for the thread
        conn = mysql.connection
        cursor = conn.cursor(MySQLdb.cursors.DictCursor)
        try:
            cursor.execute("""
                INSERT INTO repositories (user_id, name, url, status, last_scan) 
                VALUES (%s, %s, %s, 'scanning', NOW())
                ON DUPLICATE KEY UPDATE status='scanning', last_scan=NOW(), total_vulnerabilities=0, high_vuln=0, medium_vuln=0, low_vuln=0, score=0
            """, (user_id, repo_name, repo_url))
            conn.commit()
            
            cursor.execute("SELECT id FROM repositories WHERE user_id = %s AND url = %s", (user_id, repo_url))
            repo_id = cursor.fetchone()['id']

            cursor.execute("DELETE FROM vulnerabilities WHERE repo_id = %s", (repo_id,))
            conn.commit()
            print(f"Starting scan for repository: {repo_url} (ID: {repo_id})")
            subprocess.run(["python", "main-git.py", "--repo_url", repo_url], check=True, cwd=".", capture_output=True, text=True)
            print(f"Semgrep Scan completed for repository: {repo_url} (ID: {repo_id})")
            subprocess.run(["python", "ai-main.py"], check=True, cwd=".", capture_output=True, text=True)
            print(f"Ai Scan completed for repository: {repo_url} (ID: {repo_id})")

            with open("semgrep_results_analyzed.json", "r") as f:
                scan_results = json.load(f)

            total_vulnerabilities = len(scan_results.get('results', []))
            vulnerability_counts = {'high': 0, 'medium': 0, 'low': 0}
            
            for finding in scan_results['results']:
                severity = finding['extra']['metadata'].get('impact', 'low').lower()
                if severity in vulnerability_counts:
                    vulnerability_counts[severity] += 1
                
                cursor.execute("""
                    INSERT INTO vulnerabilities (repo_id, severity, title, description, file, line, remediation, false_positive_analysis)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (repo_id, severity, finding['extra']['message'], finding['extra']['message'],
                      finding['path'], finding['start']['line'],
                      finding['extra'].get('llm_code_remediation', 'No remediation provided.'),
                      finding['extra'].get('llm_false_positive_analysis', 'No false positive analysis provided.')))
            
            score = calculate_score(vulnerability_counts)
            cursor.execute("""
                UPDATE repositories
                SET status = 'completed',
                    total_vulnerabilities = %s,
                    high_vuln = %s,
                    medium_vuln = %s,
                    low_vuln = %s,
                    score = %s
                    last_scan = NOW()
                WHERE id = %s
            """, (total_vulnerabilities, vulnerability_counts['high'], vulnerability_counts['medium'], vulnerability_counts['low'], score, repo_id))
            conn.commit()
            print("Scan completed and results saved to database.")

        except subprocess.CalledProcessError as e:
            print(f"Subprocess error during scan for {repo_url}:")
            print(f"Return Code: {e.returncode}")
            print(f"Command: {e.cmd}")
            print(f"Stdout: {e.stdout}")
            print(f"Stderr: {e.stderr}")
            if repo_id:
                cursor.execute("UPDATE repositories SET status = 'error' WHERE id = %s", (repo_id,))
                conn.commit()
        except FileNotFoundError as e:
            print(f"File not found error (e.g., semgrep_results.json): {e}")
            if repo_id:
                cursor.execute("UPDATE repositories SET status = 'error' WHERE id = %s", (repo_id,))
                conn.commit()
        except json.JSONDecodeError as e:
            print(f"JSON decode error in scan results: {e}")
            if repo_id:
                cursor.execute("UPDATE repositories SET status = 'error' WHERE id = %s", (repo_id,))
                conn.commit()
        except Exception as e:
            print(f"An unexpected error occurred during scan for {repo_url}: {e}")
            if repo_id:
                cursor.execute("UPDATE repositories SET status = 'error' WHERE id = %s", (repo_id,))
                conn.commit()
        

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
    try:
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        user = cursor.fetchone()
        if user:
            return jsonify({'error': 'Account already exists!'}), 409

        hashed_pw = hash_password(password)
        cursor.execute('INSERT INTO users (name, email, password) VALUES (%s, %s, %s)', 
                      (name, email, hashed_pw))
        mysql.connection.commit()
        
        cursor.execute('SELECT * FROM users WHERE email = %s', (email,))
        new_user = cursor.fetchone()
        
        session.clear()
        session['user_id'] = new_user['id']
        session.permanent = True
        
        response = jsonify({
            'message': 'You have successfully registered!',
            'user': {
                'id': new_user['id'],
                'email': new_user['email'],
                'name': new_user['name']
            }
        })

        return response, 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')

    if not (email and password):
        return jsonify({'error': 'Please fill in all fields'}), 400

    hashed_pw = hash_password(password)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute('SELECT * FROM users WHERE email = %s AND password = %s', (email, hashed_pw))
        user = cursor.fetchone()
        
        if user:
            session.clear()
            session['user_id'] = user['id']
            session.permanent = True
            print(f"Session after login: {session}")
            response = jsonify({
                'message': 'Logged in successfully!',
                'user': {
                    'id': user['id'],
                    'email': user['email'],
                    'name': user['name']
                }
            })
            
            return response, 200
        else:
            return jsonify({'error': 'Incorrect email/password!'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        
@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully'}), 200

@app.route('/api/add_repository', methods=['POST'])
def add_repository():
    print(f"Session on add_repository page: {session}")
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized user id not found'}), 401
    
    data = request.json
    repo_url = data.get('repoUrl', '').strip()

    if not repo_url:
        return jsonify({'error': 'Repository URL is required'}), 400

    github_regex = r'^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/?$'
    match = re.match(github_regex, repo_url)
    if not match:
        return jsonify({'error': 'Invalid GitHub repository URL'}), 400
        
    owner, repo_name = match.group(1), match.group(2)
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    
    try:
        resp = requests.get(api_url, timeout=5)
        if resp.status_code != 200:
            return jsonify({'error': 'Repository does not exist or is private'}), 400
    except requests.exceptions.RequestException:
        return jsonify({'error': 'Failed to connect to GitHub API. Please check your internet connection.'}), 500

    user_id = session['user_id']
    threading.Thread(target=run_scan_pipeline, args=(repo_url, user_id)).start()

    return jsonify({'message': 'Scan started successfully!'}), 201

@app.route('/api/repositories', methods=['GET'])
def get_repositories():
    print(f"Session on repositories: {session}")
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
        
    user_id = session['user_id']
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM repositories WHERE user_id = %s", (user_id,))
        repositories = cursor.fetchall()
        
        formatted_repos = []
        for repo in repositories:
            formatted_repos.append({
                'name': repo['name'],
                'url': repo['url'],
                'status': repo['status'],
                'lastScan': repo['last_scan'].isoformat() if repo['last_scan'] else None,
                'totalVulnerabilities': repo['total_vulnerabilities'],
                'vulnerabilities': {
                    'high': repo['high_vuln'],
                    'medium': repo['medium_vuln'],
                    'low': repo['low_vuln']
                },
                'score': repo['score']
            })
        return jsonify(formatted_repos), 200
    finally:
        cursor.close()

@app.route('/api/repository_details', methods=['GET'])
def get_repository_details():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    repo_url_encoded = request.args.get('repo_url_encoded')
    if not repo_url_encoded:
        return jsonify({'error': 'Repository URL is required'}), 400

    repo_url = urllib.parse.unquote(repo_url_encoded)
    user_id = session['user_id']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        cursor.execute("SELECT * FROM repositories WHERE user_id = %s AND url = %s", (user_id, repo_url))
        repo = cursor.fetchone()
        if not repo:
            return jsonify({'error': 'Repository not found'}), 404
            
        cursor.execute("SELECT * FROM vulnerabilities WHERE repo_id = %s", (repo['id'],))
        vulnerabilities = cursor.fetchall()
        
        formatted_repo = {
            'name': repo['name'],
            'url': repo['url'],
            'status': repo['status'],
            'lastScan': repo['last_scan'].isoformat() if repo['last_scan'] else None,
            'totalVulnerabilities': repo['total_vulnerabilities'],
            'vulnerabilities': {
                'high': repo['high_vuln'],
                'medium': repo['medium_vuln'],
                'low': repo['low_vuln']
            },
            'score': repo['score']
        }
        
        formatted_vulnerabilities = [
            {
                'severity': v['severity'],
                'title': v['title'],
                'description': v['description'],
                'file': v['file'],
                'line': v['line'],
                'remediation': v['remediation'],
                'false_positive_analysis': v['false_positive_analysis']
            } for v in vulnerabilities
        ]

        return jsonify({'repository': formatted_repo, 'vulnerabilities': formatted_vulnerabilities}), 200
    finally:
        cursor.close()

if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)