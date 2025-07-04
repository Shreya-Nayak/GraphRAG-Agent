#!/usr/bin/env python3
"""
🚀 One-click startup script for GraphRAG Test Generator
"""

import subprocess
import sys
import os
import time
from pathlib import Path

def print_banner():
    print("🤖 GraphRAG Test Case Generator")
    print("=" * 50)
    print("🚀 Starting up the system...")
    print()

def check_requirements():
    """Check if basic requirements are met"""
    print("📋 Checking requirements...")
    
    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        return False
    print("✅ Python version OK")
    
    # Check if .env file exists
    if not Path(".env").exists():
        print("❌ .env file not found!")
        print("📝 Please create .env file with your API keys")
        print("   See README.md for instructions")
        return False
    print("✅ .env file found")
    
    # Check if Docker is available
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️  Docker not found - you'll need it for Qdrant")
        
    return True

def start_qdrant():
    """Start Qdrant using Docker Compose"""
    print("🐳 Starting Qdrant database...")
    try:
        subprocess.run(["docker-compose", "up", "-d", "qdrant"], check=True)
        print("✅ Qdrant started successfully")
        time.sleep(3)  # Give Qdrant time to start
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start Qdrant: {e}")
        print("💡 Make sure Docker Desktop is running")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing Python dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def start_backend():
    """Start the FastAPI backend"""
    print("⚡ Starting FastAPI backend...")
    print("🌐 Backend will be available at: http://localhost:8000")
    print("📚 API docs will be at: http://localhost:8000/docs")
    print()
    print("🔄 Starting server (press Ctrl+C to stop)...")
    
    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped")

def main():
    """Main startup function"""
    print_banner()
    
    if not check_requirements():
        print("\n❌ Requirements not met. Please check the issues above.")
        return
    
    if not start_qdrant():
        print("\n⚠️  Qdrant failed to start, but continuing anyway...")
    
    if not install_dependencies():
        print("\n❌ Failed to install dependencies")
        return
    
    print("\n🎉 System ready! Starting backend...")
    print("📝 To start the frontend:")
    print("   1. Open a new terminal")
    print("   2. cd frontend")
    print("   3. npm install")
    print("   4. npm start")
    print()
    
    start_backend()

if __name__ == "__main__":
    main()
