#!/usr/bin/env python3
"""
🔍 Quick verification script for GraphRAG Test Generator
Run this to check if your system is properly configured
"""

import subprocess
import sys
from pathlib import Path

def print_header(title):
    print(f"\n{'='*50}")
    print(f"🔍 {title}")
    print(f"{'='*50}")

def check_python():
    """Check Python version"""
    print(f"Python version: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python 3.8+ required")
        return False

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found")
        print("💡 Create .env file with your API keys (see README.md)")
        return False
    
    print("✅ .env file found")
    
    # Check for required keys
    required_keys = ["GEMINI_API_KEY", "NEO4J_URI", "NEO4J_PASSWORD"]
    env_content = env_path.read_text()
    
    missing_keys = []
    for key in required_keys:
        if key not in env_content or f"{key}=" not in env_content:
            missing_keys.append(key)
    
    if missing_keys:
        print(f"⚠️  Missing environment variables: {', '.join(missing_keys)}")
        return False
    else:
        print("✅ All required environment variables found")
        return True

def check_packages():
    """Check if required packages are installed"""
    required_packages = [
        "fastapi", "uvicorn", "httpx", "neo4j", 
        "qdrant_client", "numpy", "tiktoken"
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n💡 Install missing packages: pip install {' '.join(missing_packages)}")
        return False
    return True

def check_qdrant():
    """Check Qdrant availability (Docker or Cloud)"""
    try:
        from config import QDRANT_MODE, QDRANT_URL, QDRANT_HOST, QDRANT_PORT
        
        if QDRANT_MODE == "cloud":
            print(f"🌐 Qdrant Cloud mode: {QDRANT_URL}")
            print("✅ Qdrant Cloud configuration found")
            # Try to import qdrant client to verify it can connect
            try:
                from qdrant_vector import QdrantVectorStore
                print("✅ Qdrant client can be imported")
                return True
            except Exception as e:
                print(f"❌ Qdrant Cloud connection test failed: {e}")
                print("💡 Check your QDRANT_URL and QDRANT_API_KEY in .env")
                return False
        else:
            print(f"🐳 Qdrant Docker mode: {QDRANT_HOST}:{QDRANT_PORT}")
            # Check if Docker is available
            try:
                result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"✅ Docker found: {result.stdout.strip()}")
                    
                    # Check if Qdrant is running
                    result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
                    if "qdrant" in result.stdout:
                        print("✅ Qdrant container is running")
                        return True
                    else:
                        print("⚠️  Qdrant container not running")
                        print("💡 Run: docker-compose up -d qdrant")
                        return False
                else:
                    print("❌ Docker command failed")
                    return False
            except FileNotFoundError:
                print("❌ Docker not found in PATH")
                print("💡 Install Docker Desktop from https://docker.com")
                return False
                
    except Exception as e:
        print(f"❌ Qdrant configuration error: {e}")
        return False

def check_config():
    """Test configuration loading"""
    try:
        from config import GEMINI_API_KEY, QDRANT_MODE, QDRANT_URL, QDRANT_HOST, QDRANT_PORT
        print("✅ Configuration loaded successfully")
        if QDRANT_MODE == "cloud":
            print(f"   Qdrant: ☁️ Cloud mode ({QDRANT_URL})")
        else:
            print(f"   Qdrant: 🐳 Docker mode ({QDRANT_HOST}:{QDRANT_PORT})")
        print(f"   Gemini API: {'✅ Set' if GEMINI_API_KEY else '❌ Missing'}")
        return bool(GEMINI_API_KEY)
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

def check_documents():
    """Check if documents directory exists"""
    docs_path = Path("documents")
    if docs_path.exists():
        doc_files = list(docs_path.glob("*.docx"))
        print(f"✅ Documents directory found with {len(doc_files)} .docx files")
        if doc_files:
            for doc in doc_files[:3]:  # Show first 3
                print(f"   📄 {doc.name}")
            if len(doc_files) > 3:
                print(f"   ... and {len(doc_files) - 3} more files")
        return True
    else:
        print("⚠️  Documents directory not found")
        print("💡 Create 'documents/' folder and add your .docx files")
        return False

def run_verification():
    """Run all verification checks"""
    print("🚀 GraphRAG Test Generator - System Verification")
    
    checks = [
        ("Python Environment", check_python),
        ("Environment Variables", check_env_file),
        ("Python Packages", check_packages),
        ("Qdrant Setup", check_qdrant),
        ("Configuration", check_config),
        ("Documents", check_documents),
    ]
    
    results = {}
    for name, check_func in checks:
        print_header(name)
        results[name] = check_func()
    
    # Summary
    print_header("Summary")
    passed = sum(results.values())
    total = len(results)
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\n📊 Score: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n🎉 All checks passed! Your system is ready to run.")
        print("💡 Next steps:")
        print("   1. Run: python start.py")
        print("   2. Open another terminal and run:")
        print("      cd frontend && npm install && npm start")
    else:
        print("\n⚠️  Some checks failed. Please fix the issues above.")
        print("📚 See README.md for detailed setup instructions")

if __name__ == "__main__":
    run_verification()
