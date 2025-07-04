#!/usr/bin/env python3
"""
🔧 Environment Troubleshooting Script
Run this if you're getting "Missing GEMINI_API_KEY" errors
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and what it contains"""
    print("🔍 Checking .env file...")
    
    env_path = Path(".env")
    if not env_path.exists():
        print("❌ .env file not found!")
        print("💡 Create .env file by copying .env.example:")
        print("   cp .env.example .env")
        return False
    
    print("✅ .env file found")
    
    # Read and check contents
    with open(env_path, 'r') as f:
        content = f.read()
    
    # Check for GEMINI_API_KEY
    if "GEMINI_API_KEY=" in content:
        # Extract the line
        for line in content.split('\n'):
            if line.startswith('GEMINI_API_KEY='):
                value = line.split('=', 1)[1]
                if value and value != "your-gemini-api-key-here":
                    print(f"✅ GEMINI_API_KEY found in .env file: {value[:10]}...")
                    return True
                else:
                    print("❌ GEMINI_API_KEY is empty or placeholder")
                    print("💡 Update .env with your real Gemini API key")
                    return False
    else:
        print("❌ GEMINI_API_KEY not found in .env file")
        return False

def test_dotenv_loading():
    """Test if dotenv can load the environment"""
    print("\n🔧 Testing dotenv loading...")
    
    # Clear any existing environment variable
    if 'GEMINI_API_KEY' in os.environ:
        del os.environ['GEMINI_API_KEY']
    
    # Load with dotenv
    load_dotenv(override=True)
    
    # Check if loaded
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        print(f"✅ dotenv successfully loaded GEMINI_API_KEY: {api_key[:10]}...")
        return True
    else:
        print("❌ dotenv failed to load GEMINI_API_KEY")
        return False

def check_working_directory():
    """Check if we're in the right directory"""
    print("\n📁 Checking working directory...")
    
    cwd = Path.cwd()
    print(f"Current directory: {cwd}")
    
    # Check for key files
    key_files = ['main.py', 'config.py', '.env', 'requirements.txt']
    missing = []
    
    for file in key_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing.append(file)
    
    if missing:
        print(f"💡 Missing files: {missing}")
        print("💡 Make sure you're in the GraphRAG project directory")
        return False
    
    return True

def test_manual_loading():
    """Test manual environment loading"""
    print("\n🧪 Testing manual .env loading...")
    
    try:
        # Read .env manually
        with open('.env', 'r') as f:
            lines = f.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith('GEMINI_API_KEY=') and not line.startswith('#'):
                value = line.split('=', 1)[1]
                print(f"✅ Found in file: GEMINI_API_KEY={value[:10]}...")
                
                # Set manually
                os.environ['GEMINI_API_KEY'] = value
                print(f"✅ Set manually: {os.getenv('GEMINI_API_KEY')[:10]}...")
                return True
        
        print("❌ GEMINI_API_KEY not found or commented out")
        return False
        
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
        return False

def main():
    """Run all checks"""
    print("🚀 GraphRAG Environment Troubleshooting")
    print("=" * 50)
    
    checks = [
        ("Working Directory", check_working_directory),
        (".env File", check_env_file),
        ("dotenv Loading", test_dotenv_loading),
        ("Manual Loading", test_manual_loading),
    ]
    
    results = {}
    for name, check_func in checks:
        print(f"\n{'='*20}")
        print(f"🔍 {name}")
        print(f"{'='*20}")
        results[name] = check_func()
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 SUMMARY")
    print(f"{'='*50}")
    
    for name, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    passed = sum(results.values())
    total = len(results)
    
    if passed == total:
        print(f"\n🎉 All checks passed! Try running the app again.")
    else:
        print(f"\n⚠️  {total - passed} issues found. Fix the ❌ items above.")
        print("\n💡 Common solutions:")
        print("   1. Make sure you're in the right directory")
        print("   2. Copy .env.example to .env")
        print("   3. Add your real GEMINI_API_KEY to .env")
        print("   4. Remove any # comments from GEMINI_API_KEY line")

if __name__ == "__main__":
    main()
