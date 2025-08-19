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
import logging
import tempfile
import shutil
from groq import Groq

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Flask & DB config
app = Flask(__name__)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# IMPORTANT: Replaced with a strong, random, and unique secret key.
# This is crucial for securing Flask sessions. Do NOT share this in production.
app.secret_key = os.urandom(24).hex() # Generates a random 48-character hex string

# MySQL configuration - Update these for your setup
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'vulnguard'

mysql = MySQL(app)

# Define a default anonymous user email
DEFAULT_ANONYMOUS_USER_EMAIL = "anonymous@example.com"

# Groq API key
# IMPORTANT: Replace "gsk_..." with your actual Groq API key.
GROQ_API_KEY = "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" 

# Global variable to store the anonymous user's actual ID once fetched/created
# This prevents repeated DB queries for the anonymous user's ID
ANONYMOUS_USER_DB_ID = None

# Create tables if they don't exist
def init_db():
    """
    Initializes the MySQL database by creating 'users' and 'vulnerabilities' tables
    if they do not already exist. It also ensures a default anonymous user exists
    and retrieves its assigned ID.
    """
    global ANONYMOUS_USER_DB_ID # Declare intent to modify global variable
    try:
        cursor = mysql.connection.cursor()
        
        # Create users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create vulnerabilities table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vulnerabilities (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                repo_url TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                file_path TEXT,
                line_number INT,
                severity VARCHAR(50),
                cve VARCHAR(100),
                remediation TEXT,
                false_positive_analysis TEXT,
                scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            )
        """)
        
        # Ensure anonymous user exists and get its ID
        cursor.execute("SELECT id FROM users WHERE email = %s", (DEFAULT_ANONYMOUS_USER_EMAIL,))
        anon_user = cursor.fetchone()

        if not anon_user:
            # If anonymous user doesn't exist, create it. Let AUTO_INCREMENT assign the ID.
            anonymous_password_hash = hashlib.sha256("anonymous_secure_password_please_change".encode()).hexdigest()
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (%s, %s, %s)",
                ('anonymous', DEFAULT_ANONYMOUS_USER_EMAIL, anonymous_password_hash)
            )
            mysql.connection.commit() # Commit immediately after inserting the user
            ANONYMOUS_USER_DB_ID = cursor.lastrowid # Get the newly assigned ID
            logging.info(f"Inserted default anonymous user with ID {ANONYMOUS_USER_DB_ID}")
        else:
            ANONYMOUS_USER_DB_ID = anon_user['id']
            logging.info(f"Default anonymous user with ID {ANONYMOUS_USER_DB_ID} already exists.")

        mysql.connection.commit() # Commit any remaining changes (e.g., table creations)
        logging.info("Database tables and default user initialized successfully")
    except Exception as e:
        logging.error(f"Error initializing database: {e}")

# Initialize database on startup
with app.app_context():
    init_db()

# ---------------- AUTH FUNCTIONS ----------------

@app.route('/api/register', methods=['POST'])
def register():
    """
    Handles user registration by taking username, email, and password.
    Hashes the password and stores user details in the database.
    Logs the user in upon successful registration.
    """
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
    try:
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
    except Exception as e:
        logging.error(f"Database error during registration: {e}")
        mysql.connection.rollback()
        return jsonify({'error': 'An internal server error occurred during registration.'}), 500
    finally:
        cursor.close()


@app.route('/api/login', methods=['POST'])
def login():
    """
    Handles user login by verifying email and password.
    Sets session variables upon successful authentication.
    """
    data = request.json
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    password_hash = hashlib.sha256(password.encode()).hexdigest()

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
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

        print("Session contents after successful login:", session)

        return jsonify({'message': 'Login successful', 'user': user})
    except Exception as e:
        logging.error(f"Database error during login: {e}")
        return jsonify({'error': 'An internal server error occurred during login.'}), 500
    finally:
        cursor.close()


@app.route('/api/logout', methods=['POST'])
def logout():
    """Clears session data on user logout."""
    session.clear()
    return jsonify({'message': 'Logged out successfully'})

# ---------------- HELPER FUNCTION FOR AI ANALYSIS ----------------
def analyze_finding(client, result):
    """
    Analyzes a single Semgrep finding using the Groq API to provide
    false positive analysis and code remediation suggestions.
    """
    check_id = result.get('check_id')
    path = result.get('path')
    start_line = result.get('start', {}).get('line')
    end_line = result.get('end', {}).get('line')
    message = result.get('extra', {}).get('message')
    code_snippet = result.get('extra', {}).get('lines')

    prompt = (
        f"You are a helpful security analyst. Analyze the following security finding from a Semgrep scan:\n\n"
        f"File: {path}\n"
        f"Lines: {start_line}-{end_line}\n"
        f"Check ID: {check_id}\n"
        f"Message: {message}\n\n"
        f"Code Snippet:\n```\n{code_snippet}\n```\n\n"
        f"Please provide your analysis in the following format:\n"
        f"1.  **False Positive Analysis:** Based on the code and the finding, is this a likely "
        f"false positive? Please explain your reasoning.\n"
        f"2.  **Code Remediation:** If this is a true positive, provide a secure code "
        f"remediation. The remediation should be a drop-in replacement for the snippet if possible."
    )

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        
        content = chat_completion.choices[0].message.content
        
        false_positive_analysis = "Not found in response."
        remediation = "Not found in response."

        if "False Positive Analysis:" in content:
            parts = content.split("False Positive Analysis:")
            if len(parts) > 1:
                sub_parts = parts[1].split("Code Remediation:")
                false_positive_analysis = sub_parts[0].strip()
        
        if "Code Remediation:" in content:
            parts = content.split("Code Remediation:")
            if len(parts) > 1:
                remediation = parts[1].strip()
            
        return false_positive_analysis, remediation

    except Exception as e:
        logging.error(f"An unexpected error occurred with the Groq API: {e}")
        return None, None

# ---------------- HELPER FUNCTION FOR SCORING ----------------
def calculate_risk_score(vulnerabilities):
    """
    Calculates a risk score based on the severity of vulnerabilities.
    High = 10, Medium = 6, Low = 3
    The score is a percentage of the total possible risk score.
    A score of 100 means no vulnerabilities found.
    """
    total_score = 0
    total_possible_score = 0

    # Assign points based on severity and calculate total possible score
    for vuln in vulnerabilities:
        # Check if 'severity' key exists and is not None
        if 'severity' in vuln and vuln['severity']:
            total_possible_score += 10 # Max points for any vulnerability is 10
            severity = vuln['severity'].lower()
            if severity == 'high':
                total_score += 10
            elif severity == 'medium':
                total_score += 6
            elif severity == 'low':
                total_score += 3
        else:
            logging.warning(f"Vulnerability missing 'severity' key: {vuln}")
    
    # Calculate final score as a percentage
    if total_possible_score == 0:
        return 100 # No vulnerabilities or no valid severities, so the score is 100 (safe)
    
    # Ensure score is within 0-100 range
    score = int((total_score / total_possible_score) * 100)
    return max(0, min(100, score)) # Clamp between 0 and 100

# ---------------- REPO SCANNING ----------------

@app.route('/api/add_repository', methods=['POST'])
def add_repository():
    """
    Adds and scans a repository using Git for cloning, Semgrep for static analysis,
    and Groq for AI-driven vulnerability analysis and remediation.
    Stores the results in the database.
    """
    # Determine user_id: If logged in, use session ID.
    # If not logged in, try to use the global anonymous ID.
    user_id = session.get('user_id') 

    # If user_id is still None (not logged in and global ANONYMOUS_USER_DB_ID might not be set)
    if user_id is None:
        if ANONYMOUS_USER_DB_ID is None:
            # Fallback: Query the database to get the anonymous user's ID
            try:
                cursor_anon = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
                cursor_anon.execute("SELECT id FROM users WHERE email = %s", (DEFAULT_ANONYMOUS_USER_EMAIL,))
                anon_user_from_db = cursor_anon.fetchone()
                if anon_user_from_db:
                    user_id = anon_user_from_db['id']
                    logging.info(f"Retrieved anonymous user ID {user_id} from DB for current request.")
                else:
                    logging.error("Anonymous user not found in database during add_repository. Database integrity issue. Please ensure anonymous user is created.")
                    return jsonify({'error': 'Server configuration error: Anonymous user not found in database.'}), 500
            except Exception as e:
                logging.error(f"Database error while retrieving anonymous user ID in add_repository: {e}")
                return jsonify({'error': 'An internal server error occurred while validating user.'}), 500
            finally:
                if 'cursor_anon' in locals() and cursor_anon:
                    cursor_anon.close()
        else:
            user_id = ANONYMOUS_USER_DB_ID # Use the globally stored anonymous ID

    # Final check: user_id must be valid at this point
    if user_id is None: 
        logging.error("Repository add failed: User ID could not be determined for the request.")
        return jsonify({'error': 'Server configuration error: User ID could not be assigned.'}), 500

    user_email = session.get('email', DEFAULT_ANONYMOUS_USER_EMAIL) # Keep user_email logic as is.
    
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
    repo_directory_name = f"{owner}-{repo_name}" # Directory name for the cloned repo
    
    # Check if repo exists on GitHub
    api_url = f"https://api.github.com/repos/{owner}/{repo_name}"
    try:
        resp = requests.get(api_url, timeout=10)
        if resp.status_code != 200:
            logging.warning("Repository add failed: GitHub repo %s does not exist or is private (status %s) for user %s", repo_url, resp.status_code, user_email)
            return jsonify({'error': 'Repository does not exist or is private'}), 400
    except requests.exceptions.RequestException as req_ex:
        logging.error("Repository add failed: Could not connect to GitHub API for %s by user %s. Error: %s", repo_url, user_email, str(req_ex))
        return jsonify({'error': 'Could not connect to GitHub API. Please check your internet connection or try again later.'}), 500

    # Save current working directory to restore it later
    current_working_directory = os.getcwd() 

    # Create a temporary working directory for cloning and scanning
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            os.chdir(temp_dir) # Change to the temporary directory

            # Step 1: Git clone the repository
            logging.info("Cloning repository %s into %s", repo_url, temp_dir)
            subprocess.run(
                ["git", "clone", "--depth", "1", repo_url, repo_directory_name],
                check=True, # Raise an exception if the command fails
                capture_output=True,
                text=True
            )
            logging.info("Repository cloned successfully.")
            
            # Step 2: Run Semgrep
            semgrep_results_path = "semgrep_results.json"
            logging.info("Running Semgrep scan on %s", repo_directory_name)

            # Find the semgrep executable dynamically
            semgrep_cmd = shutil.which("semgrep")
            if not semgrep_cmd:
                logging.error("Semgrep executable not found in PATH.")
                return jsonify({'error': 'Semgrep command not found. Please ensure Semgrep is installed and in your system\'s PATH.'}), 500

            subprocess.run(
                [semgrep_cmd, f"./{repo_directory_name}", "--json", "--output", semgrep_results_path],
                check=True,
                capture_output=True,
                text=True
            )
            logging.info("Semgrep scan completed.")
            
            # Check if semgrep_results.json exists and has content
            if not os.path.exists(semgrep_results_path) or os.stat(semgrep_results_path).st_size == 0:
                logging.warning("Semgrep scan did not produce a valid results.json or it was empty for repo %s (User: %s).", repo_url, user_email)
                # If no results, still return success but with a 100% risk score
                return jsonify({'message': 'Repository scanned. No vulnerabilities found.', 'risk_score': 100}), 200
            
            # Step 3: AI analysis
            try:
                groq_client = Groq(api_key=GROQ_API_KEY)
                logging.info("Groq client initialized successfully for AI analysis.")
            except Exception as e:
                logging.error(f"Failed to initialize Groq client: {e}")
                return jsonify({'error': 'Failed to initialize AI analysis client. Check Groq API key and network connection.'}), 500

            with open(semgrep_results_path, 'r') as f:
                semgrep_data = json.load(f)
            
            results = semgrep_data.get('results', [])
            logging.info("Number of Semgrep findings to analyze with AI: %d", len(results))

            for result in results:
                logging.debug("Analyzing finding in: %s:%s", result.get('path'), result.get('start', {}).get('line'))
                false_positive_analysis, remediation = analyze_finding(groq_client, result)

                if 'extra' not in result:
                    result['extra'] = {}
                
                result['extra']['llm_false_positive_analysis'] = false_positive_analysis
                result['extra']['llm_code_remediation'] = remediation
            
            # Step 4: Calculate the risk score
            # The calculate_risk_score function expects a list of dictionaries with a 'severity' key.
            vulnerabilities_for_scoring = []
            for finding in results:
                severity = 'unknown'
                if 'extra' in finding and 'metadata' in finding['extra']:
                    impact = finding['extra']['metadata'].get('impact', '').lower()
                    if impact in ['high', 'medium', 'low']:
                        severity = impact
                vulnerabilities_for_scoring.append({'severity': severity})

            risk_score = calculate_risk_score(vulnerabilities_for_scoring)
            logging.info("Calculated risk score for %s: %s", repo_url, risk_score)

            # Optional: Save analyzed results to a new file (for debugging/review)
            # analyzed_file_path = "semgrep_results_analyzed.json"
            # with open(analyzed_file_path, "w") as f:
            #     json.dump(semgrep_data, f, indent=2)
            # logging.info("AI analysis complete. Results saved to %s", analyzed_file_path)
            
            # Step 5: Save to DB
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            
            # Clear existing vulnerabilities for this repo and user before inserting new ones.
            # This ensures rescans update the data correctly.
            cursor.execute("DELETE FROM vulnerabilities WHERE user_id = %s AND repo_url = %s", (user_id, repo_url))
            logging.info("Cleared existing vulnerabilities for repo %s (User: %s)", repo_url, user_email)
            
            # Insert new vulnerabilities
            if results: # Only insert if there are actual findings
                for finding in results:
                    title = finding.get('extra', {}).get('message', 'No Title Provided')
                    description = finding.get('extra', {}).get('llm_false_positive_analysis', 'No False Positive Analysis provided.')
                    remediation = finding.get('extra', {}).get('llm_code_remediation', 'No remediation provided.')
                    # Clean up file_path to be relative to the repo root
                    file_path = finding.get('path', 'N/A').replace(f"{repo_directory_name}{os.sep}", "", 1)
                    line_number = finding.get('start', {}).get('line', 0)
                    
                    severity = 'unknown'
                    if 'extra' in finding and 'metadata' in finding['extra']:
                        impact = finding['extra']['metadata'].get('impact', '').lower()
                        if impact in ['high', 'medium', 'low']:
                            severity = impact
                    
                    cve = finding.get('cve_id') if 'cve_id' in finding else None

                    cursor.execute("""
                        INSERT INTO vulnerabilities (user_id, repo_url, title, description, file_path, line_number, severity, cve, remediation, false_positive_analysis)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, repo_url, title, description, file_path, line_number, severity, cve, remediation, description))

                mysql.connection.commit()
                logging.info("Analysis results saved to DB for user %s, repo %s", user_email, repo_url)
            else:
                logging.info("No vulnerabilities found, so no data inserted into the database for repo %s (User: %s).", repo_url, user_email)
            
        except subprocess.CalledProcessError as e:
            logging.error(f"Subprocess execution failed. Command: {e.cmd}. Return Code: {e.returncode}. Stdout: {e.stdout}. Stderr: {e.stderr}")
            # Ensure we change back to the original directory on error before returning
            os.chdir(current_working_directory) 
            return jsonify({'error': f'Scan or git process failed. Details: {e.stderr.strip()}'}), 500
        except FileNotFoundError as e:
            logging.error(f"Required command not found: {str(e)}. Please ensure Git and Semgrep are installed and in your system\'s PATH.")
            # Ensure we change back to the original directory on error before returning
            os.chdir(current_working_directory)
            return jsonify({'error': f'A required command was not found on the server. Make sure Git and Semgrep are in your PATH.'}), 500
        except json.JSONDecodeError as e:
            logging.error(f"Error decoding JSON from a file: {str(e)}. Check Semgrep output format.")
            # Ensure we change back to the original directory on error before returning
            os.chdir(current_working_directory)
            return jsonify({'error': 'Error processing analysis results: Invalid JSON output from scan.'}), 500
        except Exception as ex:
            logging.exception(f"An unexpected error occurred during repository analysis for repo {repo_url} (User: {user_email}): {str(ex)}")
            # Ensure we change back to the original directory on error before returning
            os.chdir(current_working_directory)
            return jsonify({'error': f'An unexpected server error occurred during analysis: {str(ex)}'}), 500
        finally:
            # This ensures we always change back to the original working directory
            # regardless of whether an exception occurred in the try block.
            # It's inside the 'with' block, so temp_dir is still valid here.
            os.chdir(current_working_directory)
            
    return jsonify({'message': 'Repository scanned and saved successfully!', 'risk_score': risk_score}), 201


# ---------------- FETCH FUNCTIONS (No Authentication Required) ----------------

@app.route('/api/repositories', methods=['GET'])
def get_repositories():
    """
    Fetches a summary of all scanned repositories available for public viewing.
    Includes vulnerability counts and calculated risk scores.
    """
    logging.info("Fetching all repositories (unauthenticated access).")

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # The query now selects all repositories, without filtering by user_id
        cursor.execute("""
            SELECT
                v.repo_url,
                MAX(v.scan_date) AS last_scan,
                COUNT(v.id) AS total_vulnerabilities,
                SUM(CASE WHEN v.severity = 'high' THEN 1 ELSE 0 END) AS high_count,
                SUM(CASE WHEN v.severity = 'medium' THEN 1 ELSE 0 END) AS medium_count,
                SUM(CASE WHEN v.severity = 'low' THEN 1 ELSE 0 END) AS low_count
            FROM vulnerabilities v
            GROUP BY v.repo_url
            ORDER BY last_scan DESC
        """)
        repos_summary = cursor.fetchall()

        formatted_repos = []
        for repo in repos_summary:
            # Extract repo name from URL
            repo_name_match = re.search(r'github\.com\/[a-zA-Z0-9_.-]+\/([a-zA-Z0-9_.-]+)', repo['repo_url'])
            repo_name = repo_name_match.group(1) if repo_name_match else repo['repo_url'].split('/')[-1]

            # Fetch vulnerabilities for scoring
            cursor.execute("SELECT severity FROM vulnerabilities WHERE repo_url = %s", (repo['repo_url'],))
            vulnerabilities_for_scoring = cursor.fetchall() # Fetch all vulnerabilities for this repo

            risk_score = calculate_risk_score(vulnerabilities_for_scoring)

            formatted_repos.append({
                'id': encode_url_for_frontend(repo['repo_url']),
                'name': repo_name,
                'url': repo['repo_url'],
                'lastScan': repo['last_scan'].isoformat() if repo['last_scan'] else None,
                'vulnerabilities': {
                    'high': int(repo['high_count']),
                    'medium': int(repo['medium_count']),
                    'low': int(repo['low_count'])
                },
                'totalVulnerabilities': int(repo['total_vulnerabilities']),
                'status': 'completed',
                'risk_score': risk_score
            })

        logging.info("Successfully fetched %d repositories for unauthenticated access.", len(formatted_repos))
        return jsonify(formatted_repos), 200
    except Exception as e:
        logging.error(f"Database error during get_repositories: {e}")
        return jsonify({'error': 'An internal server error occurred while fetching repositories.'}), 500
    finally:
        cursor.close()

@app.route('/api/repository_details', methods=['GET'])
def get_repository_details():
    """
    Fetches detailed AI vulnerability results for a specific repository.
    Includes individual findings and overall repository summary with risk score.
    """
    repo_url_encoded = request.args.get('repo_url_encoded') # Get the encoded URL from frontend

    if not repo_url_encoded:
        logging.warning("Repository details failed: Missing encoded repository URL for unauthenticated access.")
        return jsonify({'error': 'Encoded Repository URL is required'}), 400

    repo_url = decode_url_from_frontend(repo_url_encoded) # Decode the URL for DB query
    logging.info("Fetching details for repo: %s (unauthenticated access)", repo_url)

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    try:
        # Fetch all vulnerabilities for the specific repo
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
                scan_date
            FROM vulnerabilities
            WHERE repo_url = %s
            ORDER BY severity DESC, file_path, line_number
        """, (repo_url,))
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
            WHERE repo_url = %s
        """, (repo_url,))
        summary = cursor.fetchone()

        repo_name_match = re.search(r'github\.com\/[a-zA-Z0-9_.-]+\/([a-zA-Z0-9_.-]+)', repo_url)
        repo_name = repo_name_match.group(1) if repo_name_match else repo_url.split('/')[-1]

        # Calculate the risk score
        risk_score = calculate_risk_score(vulnerabilities)

        repository_data = {
            'id': repo_url_encoded,
            'name': repo_name,
            'url': repo_url,
            'status': 'completed',
            'lastScan': summary['latest_scan_date'].isoformat() if summary and summary['latest_scan_date'] else None,
            'vulnerabilities': {
                'high': int(summary['high_count']) if summary else 0,
                'medium': int(summary['medium_count']) if summary else 0,
                'low': int(summary['low_count']) if summary else 0
            },
            'totalVulnerabilities': int(summary['total_vulnerabilities']) if summary else 0,
            'risk_score': risk_score
        }

        response = {
            'repository': repository_data,
            'vulnerabilities': vulnerabilities
        }

        logging.info("Successfully fetched details for repo %s (unauthenticated access). Found %d vulnerabilities.", repo_url, len(vulnerabilities))
        return jsonify(response), 200
    except Exception as e:
        logging.error(f"Database error during get_repository_details: {e}")
        return jsonify({'error': 'An internal server error occurred while fetching repository details.'}), 500
    finally:
        cursor.close()

# Helper functions for URL encoding/decoding for frontend routing
def encode_url_for_frontend(url):
    """Encodes a URL to be safe for use as a path parameter in the frontend."""
    return url.replace('/', '__SLASH__').replace('.', '__DOT__').replace(':', '__COLON__').replace('%', '__PERCENT__').replace('?', '__QUESTION__').replace('&', '__AMP__')

def decode_url_from_frontend(encoded_url):
    """Decodes a URL from a frontend path parameter back to its original form."""
    return encoded_url.replace('__SLASH__', '/').replace('__DOT__', '.').replace('__COLON__', ':').replace('__PERCENT__', '%').replace('__QUESTION__', '?').replace('__AMP__', '&')


# Health check endpoint
@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint to confirm the API is running."""
    return jsonify({'status': 'healthy', 'message': 'Anzen API is running'}), 200


# ====== Start Server ======
if __name__ == '__main__':
    # Use 0.0.0.0 to make the server accessible from other machines on the network
    # Use debug=True for development (auto-reloads, shows debugger), set to False for production
    app.run(debug=True, host='127.0.0.1', port=5000)

