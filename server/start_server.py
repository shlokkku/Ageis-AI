#!/usr/bin/env python3
"""
Startup script for Pension AI API
This script helps configure and start the FastAPI server
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'fastapi',
        'uvicorn',
        'sqlalchemy',
        'pymysql',
        'python-jose',
        'passlib',
        'python-multipart',
        'python-dotenv'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall them with:")
        print(f"   pip install {' '.join(missing_packages)}")
        return False
    
    print("✅ All required packages are installed")
    return True

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("⚠️  No .env file found")
        print("   Copy env_template.txt to .env and configure your settings")
        return False
    
    # Read .env file
    env_vars = {}
    with open(env_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                env_vars[key] = value
    
    # Check required variables
    required_vars = [
        'SECRET_KEY',
        'DB_USER',
        'DB_PASSWORD',
        'DB_HOST',
        'DB_NAME',
        'GEMINI_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if var not in env_vars or not env_vars[var] or env_vars[var].startswith('your_'):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing or invalid environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease configure these in your .env file")
        return False
    
    print("✅ Environment configuration is valid")
    return True

def check_database():
    """Check database connectivity"""
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Please check your database configuration in .env")
        return False

def start_server():
    """Start the FastAPI server"""
    print("\n🚀 Starting Pension AI API Server...")
    
    # Set environment variables
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', '8000')
    
    try:
        # Start uvicorn server
        cmd = [
            sys.executable, '-m', 'uvicorn',
            'app.main:app',
            '--host', os.environ.get('HOST', '0.0.0.0'),
            '--port', os.environ.get('PORT', '8000'),
            '--reload'
        ]
        
        print(f"Starting server on {os.environ.get('HOST', '0.0.0.0')}:{os.environ.get('PORT', '8000')}")
        print("Press Ctrl+C to stop the server")
        print("\n" + "="*50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n\n🛑 Server stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start server: {e}")

def main():
    """Main function"""
    print("🏦 Pension AI API Server Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return 1
    
    print()
    
    # Check environment configuration
    if not check_env_file():
        return 1
    
    print()
    
    # Check database connection
    if not check_database():
        return 1
    
    print()
    
    # Start server
    start_server()
    return 0

if __name__ == "__main__":
    exit(main())
