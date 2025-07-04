#!/usr/bin/env python3
"""
Final cleanup script - removes any remaining unnecessary files
"""
import os
from pathlib import Path

def cleanup():
    print("🧹 Final cleanup for Docker Desktop setup...")
    
    # Files to remove if they exist
    cleanup_files = [
        "__pycache__",
        "*.pyc",
        ".pytest_cache",
        "test_*.py"  # Keep only test_generic.py and test_integrated_system.py
    ]
    
    current_dir = Path(".")
    
    # Remove pycache directories
    for pycache in current_dir.rglob("__pycache__"):
        if pycache.is_dir():
            print(f"🗑️  Removing {pycache}")
            import shutil
            shutil.rmtree(pycache, ignore_errors=True)
    
    # Remove .pyc files
    for pyc_file in current_dir.rglob("*.pyc"):
        print(f"🗑️  Removing {pyc_file}")
        pyc_file.unlink(missing_ok=True)
    
    print("✅ Cleanup completed!")
    
    # Show final file structure
    print("\n📁 Final project structure:")
    essential_files = [
        "main.py", "config.py", "agent.py", "models.py",
        "integrated_graphrag.py", "neo4j_graph.py", "qdrant_vector.py",
        "memory_graph.py", "embedding.py", "file_ingestion.py",
        "docker-compose.yml", "requirements.txt", "verify_system.py",
        ".env", "README.md"
    ]
    
    for file in essential_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} (missing)")

if __name__ == "__main__":
    cleanup()
