#!/usr/bin/env python3
"""
Anzen Demo Setup Script
Prepares the system for hackathon demonstration
"""

import os
import sys
import subprocess
import json
import mysql.connector
from mysql.connector import Error

def check_requirements():
    """Check if all required tools are installed"""
    print("🔍 Checking system requirements...")
    
    requirements = {
        'python3': 'python3 --version',
        'node': 'node --version',
        'npm': 'npm --version',
        'git': 'git --version',
        'mysql': 'mysql --version'
    }
    
    missing = []
    for tool, command in requirements.items():
        try:
            result = subprocess.run(command.split(), capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ {tool}: {result.stdout.strip()}")
            else:
                missing.append(tool)
        except FileNotFoundError:
            missing.append(tool)
    
    if missing:
        print(f"❌ Missing requirements: {', '.join(missing)}")
        return False
    
    # Check for Semgrep
    try:
        result = subprocess.run(['semgrep', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ semgrep: {result.stdout.strip()}")
        else:
            print("❌ Semgrep not found. Install with: pip install semgrep")
            return False
    except FileNotFoundError:
        print("❌ Semgrep not found. Install with: pip install semgrep")
        return False
    
    return True

def setup_database():
    """Setup MySQL database for demo"""
    print("\n🗄️  Setting up database...")
    
    # Database configuration
    config = {
        'host': 'localhost',
        'user': 'root',
        'password': 'root'  # Change this to your MySQL root password
    }
    
    try:
        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        
        # Create database
        cursor.execute("CREATE DATABASE IF NOT EXISTS vulnguard")
        print("✅ Database 'vulnguard' created/verified")
        
        # Switch to the database
        cursor.execute("USE vulnguard")
        
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
        
        connection.commit()
        print("✅ Database tables created successfully")
        
    except Error as e:
        print(f"❌ Database setup failed: {e}")
        return False
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    
    return True

def install_backend_dependencies():
    """Install Python backend dependencies"""
    print("\n🐍 Installing backend dependencies...")
    
    try:
        os.chdir('backend')
        result = subprocess.run(['pip', 'install', '-r', 'requirements.txt'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Backend dependencies installed")
        else:
            print(f"❌ Backend installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Backend setup failed: {e}")
        return False
    finally:
        os.chdir('..')
    
    return True

def install_frontend_dependencies():
    """Install Node.js frontend dependencies"""
    print("\n📦 Installing frontend dependencies...")
    
    try:
        os.chdir('frontend')
        result = subprocess.run(['npm', 'install'], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Frontend dependencies installed")
        else:
            print(f"❌ Frontend installation failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Frontend setup failed: {e}")
        return False
    finally:
        os.chdir('..')
    
    return True

def create_demo_data():
    """Create sample demo data"""
    print("\n📊 Creating demo data...")
    
    demo_repos = [
        "https://github.com/OWASP/WebGoat",
        "https://github.com/digininja/DVWA",
        "https://github.com/juice-shop/juice-shop"
    ]
    
    print("Demo repositories ready:")
    for repo in demo_repos:
        print(f"  • {repo}")
    
    return True

def check_api_keys():
    """Check if API keys are configured"""
    print("\n🔑 Checking API configuration...")
    
    # Check Groq API key in ai-main.py
    try:
        with open('ai/ai-main.py', 'r') as f:
            content = f.read()
            if 'your_actual_api_key_here' in content:
                print("⚠️  Please update your Groq API key in ai/ai-main.py")
                return False
            else:
                print("✅ Groq API key configured")
    except FileNotFoundError:
        print("❌ ai/ai-main.py not found")
        return False
    
    return True

def create_startup_scripts():
    """Create convenient startup scripts"""
    print("\n📝 Creating startup scripts...")
    
    # Backend startup script
    backend_script = """#!/bin/bash
echo "🚀 Starting Anzen Backend..."
cd backend
python app.py
"""
    
    with open('start_backend.sh', 'w') as f:
        f.write(backend_script)
    os.chmod('start_backend.sh', 0o755)
    
    # Frontend startup script
    frontend_script = """#!/bin/bash
echo "🚀 Starting Anzen Frontend..."
cd frontend
npm run dev
"""
    
    with open('start_frontend.sh', 'w') as f:
        f.write(frontend_script)
    os.chmod('start_frontend.sh', 0o755)
    
    print("✅ Startup scripts created")
    return True

def main():
    """Main setup function"""
    print("🛡️  Anzen Hackathon Demo Setup")
    print("=" * 40)
    
    steps = [
        ("System Requirements", check_requirements),
        ("Database Setup", setup_database),
        ("Backend Dependencies", install_backend_dependencies),
        ("Frontend Dependencies", install_frontend_dependencies),
        ("API Configuration", check_api_keys),
        ("Demo Data", create_demo_data),
        ("Startup Scripts", create_startup_scripts)
    ]
    
    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            sys.exit(1)
    
    print("\n🎉 Setup completed successfully!")
    print("\n🚀 To start the demo:")
    print("1. Terminal 1: ./start_backend.sh")
    print("2. Terminal 2: ./start_frontend.sh")
    print("3. Open http://localhost:5173")
    print("\n📋 Demo repositories to try:")
    print("• https://github.com/OWASP/WebGoat")
    print("• https://github.com/digininja/DVWA")
    print("• https://github.com/juice-shop/juice-shop")
    print("\n🎯 Ready for hackathon! Good luck! 🏆")

if __name__ == "__main__":
    main()