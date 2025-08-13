# Backend Integration Guide

This guide provides detailed instructions for integrating the Anzen frontend with the Flask backend and setting up the complete AI-powered vulnerability scanning system.

## 🏗️ Architecture Overview

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Flask Backend  │    │   Firestore DB  │
│                 │    │                 │    │                 │
│  • Authentication│◄──►│  • API Routes   │◄──►│  • User Data    │
│  • Dashboard    │    │  • AI Integration│    │  • Repositories │
│  • Repository   │    │  • Git Operations│    │  • Scan Results │
│    Management   │    │  • Security     │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   AI Model      │
                       │                 │
                       │  • Code Analysis│
                       │  • Vulnerability│
                       │    Detection    │
                       └─────────────────┘
```

## 🚀 Backend Setup

### 1. Project Structure

Create the following backend structure:

```
backend/
├── app.py                 # Flask application entry point
├── requirements.txt       # Python dependencies
├── config.py             # Configuration settings
├── models/               # Data models
│   ├── __init__.py
│   ├── user.py
│   └── repository.py
├── routes/               # API route handlers
│   ├── __init__.py
│   ├── auth.py          # Authentication routes
│   ├── repositories.py  # Repository management
│   └── scans.py         # Vulnerability scanning
├── services/            # Business logic
│   ├── __init__.py
│   ├── ai_scanner.py    # AI vulnerability detection
│   ├── git_service.py   # Git operations
│   └── firestore_service.py # Database operations
├── utils/               # Utility functions
│   ├── __init__.py
│   ├── validators.py    # Input validation
│   └── security.py     # Security utilities
└── ai_models/          # AI model files
    ├── vulnerability_model.pkl
    └── model_config.json
```

### 2. Dependencies (requirements.txt)

```txt
Flask==2.3.3
Flask-CORS==4.0.0
Flask-JWT-Extended==4.5.3
google-cloud-firestore==2.13.1
firebase-admin==6.2.0
requests==2.31.0
GitPython==3.1.37
scikit-learn==1.3.1
numpy==1.24.3
pandas==2.0.3
python-dotenv==1.0.0
bcrypt==4.0.1
gunicorn==21.2.0
```

### 3. Environment Configuration

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
SECRET_KEY=your-super-secret-key-here

# Firebase Configuration
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/firebase-service-account.json
FIREBASE_PROJECT_ID=your-firebase-project-id

# JWT Configuration
JWT_SECRET_KEY=your-jwt-secret-key
JWT_ACCESS_TOKEN_EXPIRES=3600

# AI Model Configuration
AI_MODEL_PATH=./ai_models/vulnerability_model.pkl
MODEL_CONFIDENCE_THRESHOLD=0.7

# GitHub Configuration (if using GitHub API)
GITHUB_TOKEN=your-github-token-optional

# CORS Configuration
FRONTEND_URL=http://localhost:5173
```

## 🔧 Flask Application Setup

### 1. Main Application (app.py)

```python
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import Config
from routes import auth_bp, repositories_bp, scans_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    CORS(app, origins=[app.config['FRONTEND_URL']])
    jwt = JWTManager(app)
    
    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(repositories_bp, url_prefix='/api/repositories')
    app.register_blueprint(scans_bp, url_prefix='/api/scans')
    
    @app.route('/api/health')
    def health_check():
        return {'status': 'healthy', 'message': 'Anzen API is running'}
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
```

### 2. Configuration (config.py)

```python
import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(seconds=int(os.environ.get('JWT_ACCESS_TOKEN_EXPIRES', 3600)))
    
    # Firebase
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    GOOGLE_APPLICATION_CREDENTIALS = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
    
    # AI Model
    AI_MODEL_PATH = os.environ.get('AI_MODEL_PATH')
    MODEL_CONFIDENCE_THRESHOLD = float(os.environ.get('MODEL_CONFIDENCE_THRESHOLD', 0.7))
    
    # Frontend
    FRONTEND_URL = os.environ.get('FRONTEND_URL', 'http://localhost:5173')
```

## 🔐 Authentication Routes (routes/auth.py)

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from services.firestore_service import FirestoreService
from utils.security import hash_password, verify_password
from utils.validators import validate_email, validate_password

auth_bp = Blueprint('auth', __name__)
db_service = FirestoreService()

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        name = data.get('name')
        
        # Validation
        if not validate_email(email):
            return jsonify({'error': 'Invalid email format'}), 400
        
        if not validate_password(password):
            return jsonify({'error': 'Password must be at least 8 characters'}), 400
        
        # Check if user exists
        if db_service.get_user_by_email(email):
            return jsonify({'error': 'User already exists'}), 409
        
        # Create user
        hashed_password = hash_password(password)
        user_data = {
            'email': email,
            'name': name,
            'password_hash': hashed_password,
            'created_at': db_service.get_timestamp()
        }
        
        user_id = db_service.create_user(user_data)
        access_token = create_access_token(identity=user_id)
        
        return jsonify({
            'access_token': access_token,
            'user': {'id': user_id, 'email': email, 'name': name}
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        # Get user
        user = db_service.get_user_by_email(email)
        if not user or not verify_password(password, user['password_hash']):
            return jsonify({'error': 'Invalid credentials'}), 401
        
        access_token = create_access_token(identity=user['id'])
        
        return jsonify({
            'access_token': access_token,
            'user': {
                'id': user['id'],
                'email': user['email'],
                'name': user['name']
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

## 📊 Repository Management (routes/repositories.py)

```python
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.firestore_service import FirestoreService
from services.git_service import GitService
from services.ai_scanner import AIScanner
from utils.validators import validate_github_url
import threading

repositories_bp = Blueprint('repositories', __name__)
db_service = FirestoreService()
git_service = GitService()
ai_scanner = AIScanner()

@repositories_bp.route('/', methods=['GET'])
@jwt_required()
def get_repositories():
    try:
        user_id = get_jwt_identity()
        repositories = db_service.get_user_repositories(user_id)
        return jsonify(repositories), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@repositories_bp.route('/', methods=['POST'])
@jwt_required()
def add_repository():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        repo_url = data.get('url')
        
        if not validate_github_url(repo_url):
            return jsonify({'error': 'Invalid GitHub URL'}), 400
        
        # Create repository record
        repo_data = {
            'user_id': user_id,
            'url': repo_url,
            'name': repo_url.split('/')[-1],
            'status': 'pending',
            'created_at': db_service.get_timestamp(),
            'last_scan': None,
            'vulnerabilities': None
        }
        
        repo_id = db_service.create_repository(repo_data)
        
        # Start scanning in background
        thread = threading.Thread(
            target=scan_repository_async,
            args=(repo_id, repo_url)
        )
        thread.start()
        
        return jsonify({'id': repo_id, 'status': 'scanning'}), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def scan_repository_async(repo_id, repo_url):
    try:
        # Update status to scanning
        db_service.update_repository(repo_id, {'status': 'scanning'})
        
        # Clone repository
        local_path = git_service.clone_repository(repo_url)
        
        # Scan for vulnerabilities
        vulnerabilities = ai_scanner.scan_directory(local_path)
        
        # Clean up local repository
        git_service.cleanup_repository(local_path)
        
        # Update repository with results
        scan_results = {
            'status': 'completed',
            'last_scan': db_service.get_timestamp(),
            'vulnerabilities': vulnerabilities,
            'total_vulnerabilities': len(vulnerabilities)
        }
        
        db_service.update_repository(repo_id, scan_results)
        
    except Exception as e:
        # Update status to error
        db_service.update_repository(repo_id, {
            'status': 'error',
            'error_message': str(e)
        })
```

## 🤖 AI Scanner Service (services/ai_scanner.py)

```python
import os
import pickle
import json
from typing import List, Dict
import ast
import re

class AIScanner:
    def __init__(self):
        self.model = self.load_model()
        self.vulnerability_patterns = self.load_patterns()
    
    def load_model(self):
        """Load the pre-trained AI model"""
        model_path = os.environ.get('AI_MODEL_PATH')
        if os.path.exists(model_path):
            with open(model_path, 'rb') as f:
                return pickle.load(f)
        return None
    
    def load_patterns(self):
        """Load vulnerability detection patterns"""
        return {
            'sql_injection': [
                r'SELECT.*FROM.*WHERE.*=.*\+',
                r'INSERT.*INTO.*VALUES.*\+',
                r'UPDATE.*SET.*=.*\+'
            ],
            'xss': [
                r'innerHTML\s*=\s*[^;]*\+',
                r'document\.write\s*\([^)]*\+',
                r'eval\s*\([^)]*\+'
            ],
            'insecure_random': [
                r'Math\.random\(\)',
                r'Random\(\)\.next'
            ],
            'weak_crypto': [
                r'MD5\(',
                r'SHA1\(',
                r'DES\('
            ]
        }
    
    def scan_directory(self, directory_path: str) -> List[Dict]:
        """Scan entire directory for vulnerabilities"""
        vulnerabilities = []
        
        for root, dirs, files in os.walk(directory_path):
            # Skip common non-source directories
            dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__']]
            
            for file in files:
                if self.is_source_file(file):
                    file_path = os.path.join(root, file)
                    file_vulns = self.scan_file(file_path)
                    vulnerabilities.extend(file_vulns)
        
        return vulnerabilities
    
    def is_source_file(self, filename: str) -> bool:
        """Check if file is a source code file"""
        extensions = ['.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.cpp', '.c', '.php']
        return any(filename.endswith(ext) for ext in extensions)
    
    def scan_file(self, file_path: str) -> List[Dict]:
        """Scan individual file for vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            # Pattern-based detection
            for vuln_type, patterns in self.vulnerability_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        line_num = content[:match.start()].count('\n') + 1
                        vulnerability = self.create_vulnerability(
                            vuln_type, file_path, line_num, match.group()
                        )
                        vulnerabilities.append(vulnerability)
            
            # AI model detection (if available)
            if self.model:
                ai_vulns = self.ai_detect_vulnerabilities(content, file_path)
                vulnerabilities.extend(ai_vulns)
        
        except Exception as e:
            print(f"Error scanning file {file_path}: {e}")
        
        return vulnerabilities
    
    def create_vulnerability(self, vuln_type: str, file_path: str, line_num: int, code_snippet: str) -> Dict:
        """Create vulnerability object"""
        vulnerability_info = {
            'sql_injection': {
                'title': 'SQL Injection Vulnerability',
                'severity': 'high',
                'description': 'Potential SQL injection found in user input handling',
                'remediation': 'Use parameterized queries or prepared statements'
            },
            'xss': {
                'title': 'Cross-Site Scripting (XSS)',
                'severity': 'high',
                'description': 'Potential XSS vulnerability in output handling',
                'remediation': 'Sanitize user input and use proper encoding'
            },
            'insecure_random': {
                'title': 'Insecure Randomness',
                'severity': 'medium',
                'description': 'Using weak random number generation',
                'remediation': 'Use cryptographically secure random functions'
            },
            'weak_crypto': {
                'title': 'Weak Cryptographic Algorithm',
                'severity': 'medium',
                'description': 'Using deprecated cryptographic algorithms',
                'remediation': 'Use modern, secure cryptographic algorithms'
            }
        }
        
        info = vulnerability_info.get(vuln_type, {
            'title': 'Security Issue',
            'severity': 'low',
            'description': 'Potential security issue detected',
            'remediation': 'Review and fix the identified issue'
        })
        
        return {
            'id': f"{vuln_type}_{hash(f'{file_path}_{line_num}')}",
            'type': vuln_type,
            'title': info['title'],
            'severity': info['severity'],
            'description': info['description'],
            'file': file_path.replace(os.getcwd(), ''),
            'line': line_num,
            'code_snippet': code_snippet.strip(),
            'remediation': info['remediation']
        }
```

## 🔥 Firestore Service (services/firestore_service.py)

```python
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import os

class FirestoreService:
    def __init__(self):
        if not firebase_admin._apps:
            cred = credentials.Certificate(os.environ.get('GOOGLE_APPLICATION_CREDENTIALS'))
            firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()
    
    def get_timestamp(self):
        return datetime.utcnow()
    
    # User operations
    def create_user(self, user_data):
        doc_ref = self.db.collection('users').document()
        user_data['id'] = doc_ref.id
        doc_ref.set(user_data)
        return doc_ref.id
    
    def get_user_by_email(self, email):
        users = self.db.collection('users').where('email', '==', email).limit(1).stream()
        for user in users:
            return user.to_dict()
        return None
    
    def get_user_by_id(self, user_id):
        doc = self.db.collection('users').document(user_id).get()
        return doc.to_dict() if doc.exists else None
    
    # Repository operations
    def create_repository(self, repo_data):
        doc_ref = self.db.collection('repositories').document()
        repo_data['id'] = doc_ref.id
        doc_ref.set(repo_data)
        return doc_ref.id
    
    def get_user_repositories(self, user_id):
        repos = self.db.collection('repositories').where('user_id', '==', user_id).stream()
        return [repo.to_dict() for repo in repos]
    
    def get_repository(self, repo_id):
        doc = self.db.collection('repositories').document(repo_id).get()
        return doc.to_dict() if doc.exists else None
    
    def update_repository(self, repo_id, update_data):
        self.db.collection('repositories').document(repo_id).update(update_data)
```

## 🔧 Frontend API Integration

Update your frontend to connect to the Flask backend:

### 1. API Service (src/services/api.js)

```javascript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

class ApiService {
  constructor() {
    this.token = localStorage.getItem('access_token');
  }

  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { Authorization: `Bearer ${this.token}` }),
      },
      ...options,
    };

    const response = await fetch(url, config);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || 'API request failed');
    }

    return data;
  }

  // Authentication
  async login(email, password) {
    const data = await this.request('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
    
    this.token = data.access_token;
    localStorage.setItem('access_token', this.token);
    return data;
  }

  async signup(name, email, password) {
    const data = await this.request('/auth/signup', {
      method: 'POST',
      body: JSON.stringify({ name, email, password }),
    });
    
    this.token = data.access_token;
    localStorage.setItem('access_token', this.token);
    return data;
  }

  // Repositories
  async getRepositories() {
    return this.request('/repositories');
  }

  async addRepository(url) {
    return this.request('/repositories', {
      method: 'POST',
      body: JSON.stringify({ url }),
    });
  }

  async getRepository(id) {
    return this.request(`/repositories/${id}`);
  }
}

export default new ApiService();
```

### 2. Environment Variables (.env)

```env
VITE_API_URL=http://localhost:5000/api
```

## 🚀 Deployment

### 1. Backend Deployment (Google Cloud Run)

Create `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8080

CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:create_app()"]
```

Deploy to Google Cloud Run:

```bash
gcloud run deploy anzen-api \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### 2. Frontend Deployment

Update the API URL in your environment variables to point to your deployed backend.

## 🔒 Security Considerations

1. **Environment Variables**: Never commit sensitive data
2. **CORS Configuration**: Restrict to your frontend domain in production
3. **JWT Security**: Use strong secret keys and appropriate expiration times
4. **Input Validation**: Validate all user inputs on both frontend and backend
5. **Rate Limiting**: Implement rate limiting for API endpoints
6. **HTTPS**: Always use HTTPS in production

## 📊 Monitoring and Logging

Consider implementing:

- **Application Monitoring**: Use tools like Google Cloud Monitoring
- **Error Tracking**: Implement error logging and tracking
- **Performance Monitoring**: Monitor API response times
- **Security Monitoring**: Track failed authentication attempts

## 🧪 Testing

Set up comprehensive testing:

```python
# tests/test_auth.py
import pytest
from app import create_app

@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_signup(client):
    response = client.post('/api/auth/signup', json={
        'name': 'Test User',
        'email': 'test@example.com',
        'password': 'testpassword123'
    })
    assert response.status_code == 201
    assert 'access_token' in response.json
```

This integration guide provides a complete foundation for connecting your React frontend with a Flask backend, implementing AI-powered vulnerability scanning, and deploying to production.