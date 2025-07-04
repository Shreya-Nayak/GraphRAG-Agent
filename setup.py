#!/usr/bin/env python3
"""
Setup script for GraphRAG Test Case Generator
Installs dependencies and sets up the system
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_docker():
    """Check if Docker is available"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """Main setup function"""
    print("🚀 GraphRAG Test Case Generator Setup")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or python_version.minor < 8:
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Install Python dependencies
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        return False
    
    # Check for Docker
    if check_docker():
        print("✅ Docker found")
        
        # Start Qdrant with Docker Compose
        if Path("docker-compose.yml").exists():
            if not run_command("docker-compose up -d qdrant", "Starting Qdrant with Docker Compose"):
                print("⚠️  Qdrant startup failed, but continuing...")
        else:
            print("⚠️  docker-compose.yml not found, skipping Qdrant setup")
    else:
        print("⚠️  Docker not found. Please install Docker to run Qdrant vector database")
        print("📝 You can install Docker from: https://docs.docker.com/get-docker/")
    
    # Check environment file
    if not Path(".env").exists():
        print("⚠️  .env file not found")
        print("📝 Please create a .env file with your credentials:")
        print("""
# Neo4j Aura DB Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# Google Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Qdrant Vector Database
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=document_chunks
        """)
    else:
        print("✅ .env file found")
    
    # Check documents folder
    docs_path = Path("documents")
    if not docs_path.exists():
        docs_path.mkdir()
        print("📁 Created documents/ folder")
        print("📝 Please add your .docx files to the documents/ folder")
    else:
        docx_files = list(docs_path.glob("*.docx"))
        print(f"📁 Found {len(docx_files)} .docx files in documents/ folder")
    
    # Frontend setup
    frontend_path = Path("frontend")
    if frontend_path.exists():
        print("🔄 Setting up frontend...")
        original_dir = os.getcwd()
        try:
            os.chdir(frontend_path)
            if not run_command("npm install", "Installing Node.js dependencies"):
                print("⚠️  Frontend setup failed, but continuing...")
        finally:
            os.chdir(original_dir)
    
    print("\n🎉 Setup completed!")
    print("\n📋 Next steps:")
    print("1. Ensure your .env file has the correct credentials")
    print("2. Add .docx documents to the documents/ folder")
    print("3. Start the backend: python -m uvicorn main:app --reload")
    print("4. Start the frontend: cd frontend && npm start")
    print("5. Open http://localhost:3000 in your browser")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
