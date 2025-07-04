#!/usr/bin/env python3
"""
Quick startup verification for GraphRAG system
"""
import asyncio
import subprocess

def check_docker():
    """Check if Docker Desktop is running"""
    try:
        result = subprocess.run(["docker", "ps"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def check_qdrant():
    """Check if Qdrant container is running"""
    try:
        result = subprocess.run(["docker", "ps", "--filter", "name=qdrant_graphrag"], capture_output=True, text=True)
        return "qdrant_graphrag" in result.stdout
    except:
        return False

async def verify_system():
    print("🔍 GraphRAG System Verification")
    print("=" * 40)
    
    # Check Docker Desktop
    print("🐳 Checking Docker Desktop...")
    if check_docker():
        print("✅ Docker Desktop is running")
        
        # Check Qdrant container
        if check_qdrant():
            print("✅ Qdrant container is running")
        else:
            print("⚠️  Qdrant container not found")
            print("📝 Run: docker-compose up -d qdrant")
    else:
        print("❌ Docker Desktop is not running")
        print("📝 Please start Docker Desktop first")
        return False
    
    # Check basic imports
    try:
        from config import GEMINI_API_KEY
        print("✅ Configuration loaded")
        print(f"   Gemini API: {'✅' if GEMINI_API_KEY else '❌'}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Check if system initializes
    try:
        from main import initialize_graph
        print("✅ System components loaded")
        print("🚀 Ready to start server!")
        return True
    except Exception as e:
        print(f"❌ System error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(verify_system())
    if success:
        print("\n📋 To start the system:")
        print("1. Ensure Docker Desktop is running")
        print("2. Start Qdrant: docker-compose up -d qdrant")
        print("3. Start backend: python -m uvicorn main:app --reload")
        print("4. Start frontend: cd frontend && npm start")
        print("5. Open: http://localhost:3000")
    else:
        print("\n❌ Please fix the issues above first")
