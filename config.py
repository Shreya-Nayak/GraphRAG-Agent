import os
from dotenv import load_dotenv

load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Neo4j Aura DB configuration
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# Qdrant configuration - supports both Docker and Cloud
QDRANT_URL = os.getenv("QDRANT_URL")  # For Qdrant Cloud
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")  # For Qdrant Cloud
QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")  # For Docker
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))  # For Docker
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "document_chunks")

# Determine Qdrant mode
QDRANT_MODE = "cloud" if QDRANT_URL else "docker"

# Assertions
assert GEMINI_API_KEY, "Missing GEMINI_API_KEY environment variable!"

# Neo4j is optional - system will fallback to in-memory if not available
print(f"📋 Configuration loaded:")
print(f"   Gemini API: {'✅' if GEMINI_API_KEY else '❌'}")
print(f"   Neo4j URI: {'✅' if NEO4J_URI else '❌ (will use fallback)'}")
if QDRANT_MODE == "cloud":
    print(f"   Qdrant: ☁️ Cloud mode ({QDRANT_URL})")
else:
    print(f"   Qdrant: 🐳 Docker mode ({QDRANT_HOST}:{QDRANT_PORT})")