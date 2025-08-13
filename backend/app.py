import os
import re
import json
import hashlib
import subprocess
import requests
import MySQLdb.cursors
from flask import Flask, request, jsonify, session
from flask_cors import CORS
from flask_mysqldb import MySQL
import logging # Import the logging module

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask & DB config
app = Flask(__name__)
CORS(app, supports_credentials=True) # Ensure this allows credentials (cookies)

# IMPORTANT: Replace this with a strong, random, and unique secret key.
# This is crucial for securing Flask sessions.
app.secret_key = "your_strong_random_secret_key_here_please_change_this!" 

# MySQL configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'vulnguard' # Ensure this matches your database name

mysql = MySQL(app)

# ---------------- AUTH FUNCTIONS ----------------

@app.route('/api/register', methods=['POST'])
def register():
    """User registration"""
    data = request.json
    username = data.get('username', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not username or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Password hashing (consider stronger algorithms like bcrypt for production)
    password_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
    existing = cursor.fetchone()
    if existing:
        return jsonify({'error': 'Email already registered'}), 409

    cursor.execute(
        "INSERT INTO users(username, email, password_hash) VALUES(%s, %s, %s)",
        (username, email, password_hash)
    )
    mysql.connection.commit()
    
    # After successful registration, log the user in by setting session
    user_id = cursor.lastrowid
    session['user_id'] = user_id
    session['username'] = username
    session['email'] = email

    return jsonify({'message': 'Registration successful', 'user': {'id': user_id, 'username': username, 'email': email}}), 201


@app.route('/api/login', methods=['POST'])
def login():
    """User login"""
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute(
        "SELECT id, username, email FROM users WHERE email=%s AND password_hash=%s",
        (email, password_hash)
    )
    user = cursor.fetchone()

    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401

    # Set session variables upon successful login
    session['user_id'] = user['id']
    session['username'] = user['username']
    session['email'] = user['email']

    return jsonify({'message': 'Login successful', 'user': user})


@app.route('/api/logout', methods=['POST'])
def logout():
    """Clear session on logout"""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})


# ---------------- REPO SCANNING ----------------

@app.route('/api/add_repository', methods=['POST'])
def add_repository():
    """Add and scan repository"""
    try:
        # Check if user is logged in via session
        if 'user_id' not in session:
            logging.warning("Unauthorized attempt to add repository.")
            return jsonify({'error': 'Unauthorized'}), 401

        user_id = session['user_id'] # Get user_id from the session
        user_email = session['email'] # Get user_email from the session for logging/DB if needed

        data = request.json
        repo_url = data.get('repoUrl', '').strip()

        if not repo_url:
            logging.warning("Repository add failed: Missing repository URL for user %s", user_email)
            return jsonify({'error': 'Repository URL is required'}), 400

        # Validate GitHub URL format
        github_regex = r'^https://github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+)/?$'
        match = re.match(github_regex, repo_url)
        if not match:
            logging.warning("Repository add failed: Invalid GitHub URL format for %s by user %s", repo_url, user_email)
            return jsonify({'error': 'Invalid GitHub repository URL'}), 400

        owner, repo_name = match.group(1), match.group(2)

        # Check if repo exists on GitHub
        api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
        try:
            resp = requests.get(api_url, timeout=5)
            if resp.status_code != 200:
                logging.warning("Repository add failed: GitHub repo %s does not exist or is private (status %s) for user %s", repo_url, resp.status_code, user_email)
                return jsonify({'error': 'Repository does not exist or is private'}), 400
        except requests.exceptions.RequestException as req_ex:
            logging.error("Repository add failed: Could not connect to GitHub API for %s by user %s. Error: %s", repo_url, user_email, str(req_ex))
            return jsonify({'error': 'Could not connect to GitHub API. Please check your internet connection or try again later.'}), 500

        # Define paths for external scripts (adjust as per your actual directory structure)
        # Using 'main-git.py' as per previous discussions, assuming 'main-git-v.py' was a typo or variant.
        # If 'main-git-v.py' is indeed a different script, adjust the path accordingly.
        main_git_script_path = r"D:\project\thupparivaalan\main-git.py" 
        ai_main_script_path = r"D:\project\thupparivaalan\ai\ai-main.py"

        # Step 1: Run main-git.py with repo url
        logging.info("Running main-git.py for repo: %s (User: %s)", repo_url, user_email)
        main_git_process = subprocess.run(
            ["python", main_git_script_path, repo_url], 
            check=True,
            capture_output=True, # Capture output for debugging
            text=True # Decode output as text
        )
        logging.info("main-git.py completed. Stdout: %s", main_git_process.stdout)

        # Check if semgrep_results.json exists after main-git.py
        if not os.path.exists("semgrep_results.json"):
            logging.error("Semgrep scan failed: semgrep_results.json not found after main-git.py execution for repo %s (User: %s). Stderr: %s", repo_url, user_email, main_git_process.stderr)
            return jsonify({'error': 'Semgrep scan failed to produce results.json. Check backend logs.'}), 500

        # Step 2: Run ai-main.py
        logging.info("Running ai-main.py (User: %s)", user_email)
        ai_main_process = subprocess.run(
            ["python", ai_main_script_path], 
            check=True, 
            capture_output=True, 
            text=True
        )
        logging.info("ai-main.py completed. Stdout: %s", ai_main_process.stdout)

        # Check if semgrep_results_analyzed.json exists after ai-main.py
        analyzed_file_path = "semgrep_results_analyzed.json"
        if not os.path.exists(analyzed_file_path):
            logging.error("AI analysis failed: %s not found after ai-main.py execution for repo %s (User: %s). Stderr: %s", analyzed_file_path, repo_url, user_email, ai_main_process.stderr)
            return jsonify({'error': 'AI analysis failed to produce analyzed results.json. Check backend logs.'}), 500

        # Step 3: Load AI analyzed results
        with open(analyzed_file_path, "r") as f:
            ai_results = json.load(f)
        logging.info("Successfully read analysis data from %s for repo %s (User: %s)", analyzed_file_path, repo_url, user_email)

        # Step 4: Save to DB (using the 'vulnerabilities' table)
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        # Clear existing vulnerabilities for this repo and user before inserting new ones
        # This ensures that rescans update the data correctly.
        cursor.execute("DELETE FROM vulnerabilities WHERE user_id = %s AND repo_url = %s", (user_id, repo_url))
        logging.info("Cleared existing vulnerabilities for repo %s (User: %s)", repo_url, user_email)
        
        for finding in ai_results.get('results', []):
            title = finding.get('extra', {}).get('message', 'No Title Provided')
            description = finding.get('extra', {}).get('llm_false_positive_analysis', 'No False Positive Analysis provided.')
            remediation = finding.get('extra', {}).get('llm_code_remediation', 'No remediation provided.')
            file_path = finding.get('path', 'N/A')
            line_number = finding.get('start', {}).get('line', 0)
            severity = finding.get('extra', {}).get('severity', 'unknown')
            cve = finding.get('cve_id') if 'cve_id' in finding else None # Assuming 'cve_id' from Semgrep output

            cursor.execute("""
                INSERT INTO vulnerabilities (user_id, repo_url, title, description, file_path, line_number, severity, cve, remediation, false_positive_analysis)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (user_id, repo_url, title, description, file_path, line_number, severity, cve, remediation, description))
        
        mysql.connection.commit()
        logging.info("Analysis results saved to DB for user %s, repo %s", user_email, repo_url)
        
        # Clean up temporary files
        if os.path.exists("semgrep_results.json"):
            os.remove("semgrep_results.json")
            logging.info("Cleaned up semgrep_results.json")
        if os.path.exists(analyzed_file_path):
            os.remove(analyzed_file_path)
            logging.info("Cleaned up %s", analyzed_file_path)
        
        return jsonify({'message': 'Repository scanned and saved successfully!'}), 201

    except subprocess.CalledProcessError as e:
        logging.error("Subprocess execution failed for repo %s (User: %s). Command: %s. Return Code: %s. Stdout: %s. Stderr: %s", 
                      repo_url, user_email, e.cmd, e.returncode, e.stdout, e.stderr)
        return jsonify({'error': f'Scan or AI process failed. Details: {e.stderr.strip()}'}), 500
    except FileNotFoundError as e:
        logging.error("Required script or file not found: %s for repo %s (User: %s). Error: %s", 
                      e.filename, repo_url, user_email, str(e))
        return jsonify({'error': f'A required script or file was not found on the server. Please contact support. ({e.filename})'}), 500
    except json.JSONDecodeError as e:
        logging.error("Error decoding JSON from analysis results for repo %s (User: %s). Error: %s", 
                      repo_url, user_email, str(e))
        return jsonify({'error': f'Error processing analysis results: Invalid JSON output from analysis scripts. ({str(e)})'}), 500
    except Exception as ex:
        logging.exception("An unexpected error occurred during repository analysis for repo %s (User: %s). Error: %s", 
                          repo_url, user_email, str(ex)) # Use exception for full traceback
        return jsonify({'error': f'An unexpected server error occurred: {str(ex)}'}), 500


# ---------------- FETCH FUNCTIONS ----------------

@app.route('/api/repositories', methods=['GET'])
def get_repositories():
    """Fetch all repositories for logged-in user with summary stats"""
    if 'user_id' not in session:
        logging.warning("Unauthorized attempt to fetch repositories.")
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    user_email = session['email']
    logging.info("Fetching repositories for user: %s", user_email)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute("""
        SELECT 
            v.repo_url, 
            MAX(v.scan_date) AS last_scan, 
            COUNT(v.id) AS total_vulnerabilities,
            SUM(CASE WHEN v.severity = 'high' THEN 1 ELSE 0 END) AS high_count,
            SUM(CASE WHEN v.severity = 'medium' THEN 1 ELSE 0 END) AS medium_count,
            SUM(CASE WHEN v.severity = 'low' THEN 1 ELSE 0 END) AS low_count
        FROM vulnerabilities v
        WHERE v.user_id = %s
        GROUP BY v.repo_url
        ORDER BY last_scan DESC
    """, (user_id,))
    repos_summary = cursor.fetchall()
    
    formatted_repos = []
    for repo in repos_summary:
        # Extract repo name from URL
        repo_name_match = re.search(r'github\.com\/[a-zA-Z0-9_.-]+\/([a-zA-Z0-9_.-]+)', repo['repo_url'])
        repo_name = repo_name_match.group(1) if repo_name_match else repo['repo_url'].split('/')[-1]

        formatted_repos.append({
            'id': encode_url_for_frontend(repo['repo_url']), # Use encoded URL for frontend routing
            'name': repo_name,
            'url': repo['repo_url'],
            'lastScan': repo['last_scan'].isoformat() if repo['last_scan'] else None, # Format datetime for JSON
            'vulnerabilities': {
                'high': int(repo['high_count']),
                'medium': int(repo['medium_count']),
                'low': int(repo['low_count'])
            },
            'totalVulnerabilities': int(repo['total_vulnerabilities']),
            'status': 'completed' # You might want a more dynamic status in the future (e.g., 'scanning', 'error')
        })
        
    logging.info("Successfully fetched %d repositories for user %s", len(formatted_repos), user_email)
    return jsonify(formatted_repos), 200

@app.route('/api/repository_details', methods=['GET'])
def get_repository_details():
    """Fetch detailed AI vulnerability results for a specific repository"""
    if 'user_id' not in session:
        logging.warning("Unauthorized attempt to fetch repository details.")
        return jsonify({'error': 'Unauthorized'}), 401

    user_id = session['user_id']
    user_email = session['email']
    repo_url_encoded = request.args.get('repo_url_encoded') # Get the encoded URL from frontend
    
    if not repo_url_encoded:
        logging.warning("Repository details failed: Missing encoded repository URL for user %s", user_email)
        return jsonify({'error': 'Encoded Repository URL is required'}), 400

    repo_url = decode_url_from_frontend(repo_url_encoded) # Decode the URL for DB query
    logging.info("Fetching details for repo: %s (User: %s)", repo_url, user_email)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
    # Fetch all vulnerabilities for the specific repo and user
    cursor.execute("""
        SELECT 
            title, 
            description, 
            file_path AS file, 
            line_number AS line, 
            severity, 
            cve, 
            remediation, 
            false_positive_analysis,
            scan_date # Include scan_date for the last scan info
        FROM vulnerabilities 
        WHERE repo_url = %s AND user_id = %s
        ORDER BY severity DESC, file_path, line_number
    """, (repo_url, user_id))
    vulnerabilities = cursor.fetchall()
    
    # Fetch summary for the repository
    cursor.execute("""
        SELECT 
            COUNT(id) AS total_vulnerabilities,
            SUM(CASE WHEN severity = 'high' THEN 1 ELSE 0 END) AS high_count,
            SUM(CASE WHEN severity = 'medium' THEN 1 ELSE 0 END) AS medium_count,
            SUM(CASE WHEN severity = 'low' THEN 1 ELSE 0 END) AS low_count,
            MAX(scan_date) AS latest_scan_date
        FROM vulnerabilities
        WHERE repo_url = %s AND user_id = %s
    """, (repo_url, user_id))
    summary = cursor.fetchone()
    
    repo_name_match = re.search(r'github\.com\/[a-zA-Z0-9_.-]+\/([a-zA-Z0-9_.-]+)', repo_url)
    repo_name = repo_name_match.group(1) if repo_name_match else repo_url.split('/')[-1]

    repository_data = {
        'id': repo_url_encoded,
        'name': repo_name,
        'url': repo_url,
        'status': 'completed', # Assuming completed after fetching data
        'lastScan': summary['latest_scan_date'].isoformat() if summary and summary['latest_scan_date'] else None,
        'vulnerabilities': {
            'high': int(summary['high_count']) if summary else 0,
            'medium': int(summary['medium_count']) if summary else 0,
            'low': int(summary['low_count']) if summary else 0
        },
        'totalVulnerabilities': int(summary['total_vulnerabilities']) if summary else 0
    }
    
    response = {
        'repository': repository_data,
        'vulnerabilities': vulnerabilities
    }
    
    logging.info("Successfully fetched details for repo %s (User: %s). Found %d vulnerabilities.", repo_url, user_email, len(vulnerabilities))
    return jsonify(response), 200


# Helper functions for URL encoding/decoding for frontend routing
def encode_url_for_frontend(url):
    """Encodes a URL to be safe for use as a path parameter in the frontend."""
    return url.replace('/', '__SLASH__').replace('.', '__DOT__').replace(':', '__COLON__').replace('%', '__PERCENT__').replace('?', '__QUESTION__').replace('&', '__AMP__')

def decode_url_from_frontend(encoded_url):
    """Decodes a URL from a frontend path parameter back to its original form."""
    return encoded_url.replace('__SLASH__', '/').replace('__DOT__', '.').replace('__COLON__', ':').replace('__PERCENT__', '%').replace('__QUESTION__', '?').replace('__AMP__', '&')


# ====== Start Server ======
if __name__ == '__main__':
    # Use 0.0.0.0 to make the server accessible from other machines on the network
    # Use debug=True for development (auto-reloads, shows debugger), set to False for production
    app.run(debug=True, host='127.0.0.1', port=5000)