import os
from dotenv import load_dotenv

# Force reload environment variables (important for switching configurations)
load_dotenv(override=True)

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Neo4j configuration - supports both Desktop and Aura
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Determine Neo4j mode
NEO4J_MODE = "aura" if NEO4J_URI and "neo4j+s://" in NEO4J_URI else "desktop"

# Qdrant configuration - supports both Docker and Cloud
QDRANT_URL = os.getenv("QDRANT_URL")  # For Qdrant Cloud
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # For Qdrant Cloud
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")  # For Docker
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))  # For Docker
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "document_chunks")

# Determine Qdrant mode
QDRANT_MODE = "cloud" if QDRANT_URL else "docker"

# Debug: Print what we're loading (helpful for troubleshooting)
print(f"🔍 Debug - Loading configuration from .env:")
print(f"   GEMINI_API_KEY found: {'Yes' if GEMINI_API_KEY else 'No'}")
if GEMINI_API_KEY:
    print(f"   GEMINI_API_KEY preview: {GEMINI_API_KEY[:10]}...")
print(f"   NEO4J_URI: {NEO4J_URI}")
print(f"   QDRANT_URL: {QDRANT_URL}")

# Assertions with better error messages
if not GEMINI_API_KEY:
    print("❌ GEMINI_API_KEY not found in environment!")
    print("💡 Make sure your .env file has:")
    print("   GEMINI_API_KEY=your-actual-api-key")
    print("💡 Check that .env file exists in the same directory as main.py")
    raise AssertionError("Missing GEMINI_API_KEY environment variable!")

# Neo4j is optional - system will fallback to in-memory if not available
print(f"📋 Configuration loaded:")
print(f"   Gemini API: {'✅' if GEMINI_API_KEY else '❌'}")
if NEO4J_URI:
    if NEO4J_MODE == "aura":
        print(f"   Neo4j: ☁️ Aura mode ({NEO4J_URI})")
    else:
        print(f"   Neo4j: 🖥️ Desktop mode ({NEO4J_URI})")
else:
    print(f"   Neo4j: ❌ (will use in-memory fallback)")

if QDRANT_MODE == "cloud":
    print(f"   Qdrant: ☁️ Cloud mode ({QDRANT_URL})")
else:
    print(f"   Qdrant: 🐳 Docker mode ({QDRANT_HOST}:{QDRANT_PORT})")