# Anzen - AI Code Vulnerability Checker

A modern, AI-powered web application that scans GitHub repositories for security vulnerabilities and provides detailed remediation guidance using Semgrep and Groq AI.

## 🚀 Features

- **User Authentication**: Secure sign-up and login system with session management
- **Repository Management**: Add, scan, and manage GitHub repositories
- **AI-Powered Analysis**: Automated vulnerability detection using Semgrep + Groq AI
- **Detailed Reports**: Comprehensive vulnerability reports with severity levels and remediation
- **Real-time Scanning**: Live scanning status and progress tracking
- **Dark Mode UI**: Professional dark theme optimized for security professionals
- **Responsive Design**: Works seamlessly across all devices

## 🛠️ Technology Stack

### Frontend
- **React 18** with hooks and modern patterns
- **React Router** for navigation
- **Tailwind CSS** with dark mode
- **Lucide React** icons
- **Vite** for fast development

### Backend
- **Flask** Python web framework
- **MySQL** database for user data and scan results
- **Semgrep** for static code analysis
- **Groq AI** (Llama 3) for vulnerability analysis
- **GitPython** for repository cloning

## 📦 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- MySQL server
- Git
- Semgrep CLI (`pip install semgrep`)

### 1. Database Setup
```sql
CREATE DATABASE vulnguard;
-- Tables will be created automatically on first run
```

### 2. Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Update database credentials in app.py:
# MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB

python app.py
```

### 3. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### 4. Configure AI Service
Update `ai/ai-main.py` with your Groq API key:
```python
api_key = "your_groq_api_key_here"
```

## 🎯 Demo Flow

1. **Sign Up/Login** - Create account or login
2. **Add Repository** - Enter GitHub repository URL
3. **Automatic Scanning** - System clones, scans with Semgrep, analyzes with AI
4. **View Results** - Detailed vulnerability report with remediation suggestions
5. **Rescan** - Re-analyze repositories for updated results

## 🔧 API Endpoints

- `POST /api/register` - User registration
- `POST /api/login` - User authentication
- `POST /api/logout` - Session cleanup
- `POST /api/add_repository` - Add and scan repository
- `GET /api/repositories` - List user repositories
- `GET /api/repository_details` - Get detailed vulnerability report

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │    │  Flask Backend  │    │   MySQL DB      │
│                 │    │                 │    │                 │
│  • Authentication│◄──►│  • API Routes   │◄──►│  • Users        │
│  • Dashboard    │    │  • Session Mgmt │    │  • Repositories │
│  • Repository   │    │  • Scan Pipeline│    │  • Vulnerabilities│
│    Management   │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Scanning Pipeline│
                       │                 │
                       │ • Git Clone     │
                       │ • Semgrep Scan  │
                       │ • AI Analysis   │
                       │ • Cleanup       │
                       └─────────────────┘
```

## 🔒 Security Features

- **Session-based Authentication** - Secure server-side sessions
- **Input Validation** - GitHub URL validation and sanitization
- **Temporary File Handling** - Automatic cleanup of cloned repositories
- **Error Handling** - Comprehensive error states and logging
- **CORS Configuration** - Properly configured cross-origin requests

## 🎨 UI/UX Highlights

- **Professional Dark Theme** - Optimized for security professionals
- **Responsive Design** - Mobile-first approach
- **Loading States** - Clear progress indicators
- **Error Handling** - User-friendly error messages
- **Micro-interactions** - Smooth animations and transitions

## 📊 Vulnerability Analysis

The system provides:
- **Severity Classification** - High, Medium, Low priority levels
- **False Positive Analysis** - AI-powered assessment of findings
- **Code Remediation** - Specific fix suggestions for each vulnerability
- **File Location** - Exact file and line number references
- **Scan History** - Track changes over time

## 🚀 Deployment Ready

- **Environment Configuration** - Easy setup for different environments
- **Docker Support** - Containerization ready
- **Logging** - Comprehensive logging for debugging
- **Health Checks** - API health monitoring endpoints

## 🎯 Hackathon Demo Script

1. **Show Landing** - Professional security-focused UI
2. **User Registration** - Quick signup process
3. **Add Repository** - Paste any public GitHub repo
4. **Live Scanning** - Watch real-time scanning progress
5. **Results Analysis** - Detailed vulnerability breakdown
6. **AI Insights** - Show AI-powered remediation suggestions
7. **VS Code Extension** - Mention the companion extension

## 🏆 Competitive Advantages

- **AI-Powered Analysis** - Goes beyond basic static analysis
- **User-Friendly Interface** - Accessible to developers of all levels
- **Comprehensive Reporting** - Detailed, actionable insights
- **Fast Scanning** - Optimized pipeline for quick results
- **Extensible Architecture** - Easy to add new analysis tools

## 📝 License

MIT License - see LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

**Built for security professionals, by security professionals.** 🛡️