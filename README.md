# GraphRAG Test Case Generator

🤖 **AI-powered test case generation using GraphRAG architecture** 

Generate comprehensive test cases from your technical documents using Google Gemini AI, Neo4j knowledge graphs, and Qdrant vector search.

![Architecture](https://img.shields.io/badge/Architecture-GraphRAG-blue) ![AI](https://img.shields.io/badge/AI-Google%20Gemini-orange) ![Database](https://img.shields.io/badge/Graph-Neo4j-green) ![Vector](https://img.shields.io/badge/Vector-Qdrant-purple)

> **🚀 Quick Setup**: Copy `.env.example` to `.env`, add your API keys, choose Docker or Cloud for Qdrant, and run `python start.py`!

## 🏗️ Architecture Overview

```
Documents (.docx) → Knowledge Graph (Neo4j) + Vector Store (Qdrant) → AI Agent (Gemini) → Test Cases
```

- **📊 Knowledge Graph**: Neo4j for storing document relationships  
  - **🖥️ Option A**: Neo4j Desktop (local, free, easy setup)
  - **☁️ Option B**: Neo4j Aura (managed cloud service)
- **🔍 Vector Database**: Qdrant for fast similarity search on embeddings
  - **☁️ Option A**: Qdrant Cloud (managed service, no setup)
  - **🐳 Option B**: Qdrant Docker (local, requires Docker)
- **🤖 AI Agent**: Google Gemini 1.5 Flash for intelligent test generation
- **⚡ Backend**: FastAPI with hybrid search (vector + graph)
- **🎨 Frontend**: React UI for interactive test case generation

## 🚀 Quick Start (5 minutes)

### Prerequisites ✅

Before you start, make sure you have:

1. **Python 3.8+** - [Download Python](https://python.org/downloads)
2. **Node.js 16+** - [Download Node.js](https://nodejs.org)
3. **Neo4j Desktop** - [Download Neo4j Desktop](https://neo4j.com/download/) OR Neo4j Aura account
4. **Qdrant Cloud account** - [Sign up at Qdrant Cloud](https://cloud.qdrant.io) OR Docker Desktop
5. **Git** - [Download Git](https://git-scm.com)

### Step 1: Clone the Repository

```bash
git clone <your-repo-url>
cd "GraphRAG Agent neo4j"
```

### Step 2: Get Required API Keys

#### 🔑 Google Gemini API Key (FREE)
1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Click "Create API Key"
3. Copy the key - you'll need it in Step 4

#### 🔑 Neo4j Setup - Choose ONE Option:

**🖥️ Option A: Neo4j Desktop (Recommended for beginners)**
- ✅ **Free and local**
- ✅ **No signup required**
- ✅ **Works offline**
- ✅ **Easy visual interface**
- **Setup**: 
  1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
  2. Create a new project and database
  3. Set a password (remember it for .env)
  4. Start the database

**☁️ Option B: Neo4j Aura (Managed cloud service)**
- ✅ **No installation needed**
- ✅ **Managed and scalable**
- ✅ **Better for production**
- ❌ Requires signup
- **Setup**: 
  1. Go to [Neo4j Aura](https://neo4j.com/aura)
  2. Create free account
  3. Create a new instance (free tier)
  4. Copy connection details

#### 🔑 Qdrant Setup - Choose ONE Option:

**☁️ Option A: Qdrant Cloud (Recommended - Default setup)**
- ✅ **No installation needed**
- ✅ **Managed and scalable**
- ✅ **Free tier available**
- ✅ **Better performance**
- **Setup**: 
  1. Go to [Qdrant Cloud](https://cloud.qdrant.io)
  2. Create free account
  3. Create a cluster
  4. Copy URL and API key

**🐳 Option B: Qdrant Docker (Local alternative)**
- ✅ **Free and local**
- ✅ **No signup required**
- ✅ **Works offline**
- ❌ Requires Docker Desktop
- **Setup**: Just run `docker-compose up -d qdrant`

### Step 3: Set Up the Environment

#### Create Python Virtual Environment
```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# macOS/Linux
python3 -m venv .venv
source .venv/bin/activate
```

#### Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory. **Choose your preferred combination:**

#### 🎯 Recommended Setup (Neo4j Desktop + Qdrant Cloud)

```env
# Neo4j Desktop (Local)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-desktop-password
NEO4J_DATABASE=neo4j

# Google Gemini API (paste your key from Step 2)
GEMINI_API_KEY=your-gemini-api-key-here

# Qdrant Cloud (Remote) - DEFAULT
QDRANT_URL=https://your-cluster-url.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION_NAME=document_chunks
```

#### 🌐 Alternative: Full Cloud Setup (Neo4j Aura + Qdrant Cloud)

```env
# Neo4j Aura (Cloud)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password-from-aura
NEO4J_DATABASE=neo4j

# Google Gemini API (paste your key from Step 2)
GEMINI_API_KEY=your-gemini-api-key-here

# Qdrant Cloud (Remote)
QDRANT_URL=https://your-cluster-url.qdrant.tech
QDRANT_API_KEY=your-qdrant-api-key-here
QDRANT_COLLECTION_NAME=document_chunks
```

#### 🐳 Alternative: Full Local Setup (Neo4j Desktop + Qdrant Docker)

```env
# Neo4j Desktop (Local)
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-desktop-password
NEO4J_DATABASE=neo4j

# Google Gemini API (paste your key from Step 2)
GEMINI_API_KEY=your-gemini-api-key-here

# Qdrant Docker (Local)
QDRANT_HOST=localhost
QDRANT_PORT=6333
QDRANT_COLLECTION_NAME=document_chunks
```

> **💡 How it works**: 
> - Neo4j: Desktop uses `bolt://`, Aura uses `neo4j+s://`
> - Qdrant: If `QDRANT_URL` is set, uses Cloud mode. Otherwise uses Docker mode.

### Step 5: Start Your Services (If using local options)

**🖥️ Neo4j Desktop users**: Make sure your database is started in Neo4j Desktop

**🐳 Qdrant Docker users**: 
```bash
# Start Qdrant in Docker (make sure Docker Desktop is running)
docker-compose up -d qdrant

# Verify it's running
docker ps
```

**☁️ Cloud users**: Skip this step - your services are already running in the cloud!

### Step 6: Start the Backend

```bash
# Run the setup script (installs dependencies and initializes system)
python setup.py

# Start the FastAPI server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**✅ Backend running at:** http://localhost:8000

### Step 7: Start the Frontend

```bash
# Open a new terminal and navigate to frontend
cd frontend

# Install Node.js dependencies
npm install

# Start React development server
npm start
```

**✅ Frontend running at:** http://localhost:3000

## 🎯 How to Use

1. **Open your browser** to http://localhost:3000
2. **Enter a test query** like:
   - "Login API should handle invalid credentials"
   - "User registration with email validation"
   - "Payment processing edge cases"
3. **Click "Generate Test Cases"**
4. **Copy the generated test cases** using the copy button

## 📁 Adding Your Documents

Put your `.docx` files in the `documents/` folder:
```
documents/
├── API_Specification.docx
├── Requirements.docx
├── Design_Document.docx
└── your-other-docs.docx
```

The system will automatically process them when it starts.

## 🛠️ Troubleshooting

### Common Issues & Solutions

#### ❌ "ModuleNotFoundError" 
**Solution:** Make sure your virtual environment is activated
```bash
# Windows
.venv\Scripts\activate

# macOS/Linux  
source .venv/bin/activate
```

#### ❌ "Qdrant connection failed"

**For Docker users:**
```bash
# Check if Docker is running
docker ps

# Start Qdrant if not running
docker-compose up -d qdrant

# Check Qdrant logs
docker logs qdrant_graphrag
```

**For Cloud users:**
- Check your `QDRANT_URL` and `QDRANT_API_KEY` in `.env` file
- Verify your Qdrant Cloud cluster is running
- Test connection at your Qdrant Cloud dashboard

#### ❌ "Neo4j connection failed"
**Solution:** Check your `.env` file has correct Neo4j credentials

#### ❌ "Frontend can't connect to backend"
**Solution:** Make sure backend is running on port 8000
```bash
# Check if backend is running
curl http://localhost:8000/health
```

#### ❌ "No test cases generated"
**Solution:** 
1. Check if documents are in `documents/` folder
2. Verify Gemini API key is valid
3. Check backend logs for errors

### Getting Help

1. **Check the logs** in your terminal for error messages
2. **Run the verification script**: `python quick_verify.py`
3. **Check service status**: 
   - Backend: http://localhost:8000/docs
   - Qdrant Docker: http://localhost:6333/dashboard
   - Qdrant Cloud: Your cloud dashboard URL

## 🔧 Advanced Configuration

### 🤔 Qdrant: Docker vs Cloud - Which to Choose?

| Feature | 🐳 Docker (Local) | ☁️ Cloud (Remote) |
|---------|-------------------|-------------------|
| **Cost** | Free | Free tier + paid plans |
| **Setup** | Requires Docker Desktop | Just signup & API key |
| **Performance** | Fast (local) | Network dependent |
| **Scalability** | Limited by your machine | Highly scalable |
| **Offline** | Works offline | Requires internet |
| **Maintenance** | You manage | Managed service |
| **Best for** | Development, testing | Production, collaboration |

**🎯 Recommendation:**
- **Beginners/Development**: Use Docker mode
- **Production/Team**: Use Cloud mode

### 🔄 Switching Between Modes

You can easily switch between Docker and Cloud modes:

1. **To switch to Cloud**: Add `QDRANT_URL` and `QDRANT_API_KEY` to `.env`
2. **To switch to Docker**: Remove/comment out `QDRANT_URL` from `.env`
3. **Restart** the application

The system automatically detects which mode to use based on your `.env` configuration.

### Optional: Neo4j Vector Index (for better performance)

If you want to use Neo4j's vector search capabilities:

1. Open Neo4j Browser (from your Aura console)
2. Run this command:
```cypher
CREATE VECTOR INDEX chunk_embeddings IF NOT EXISTS
FOR (c:Chunk) ON (c.embedding)
OPTIONS {indexConfig: {
    `vector.dimensions`: 768,
    `vector.similarity_function`: 'cosine'
}}
```

### Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `NEO4J_URI` | Neo4j Aura connection string | Yes | - |
| `NEO4J_USERNAME` | Neo4j username | Yes | `neo4j` |
| `NEO4J_PASSWORD` | Neo4j password | Yes | - |
| `GEMINI_API_KEY` | Google Gemini API key | Yes | - |
| **Qdrant Docker Mode** | | | |
| `QDRANT_HOST` | Qdrant host | No | `localhost` |
| `QDRANT_PORT` | Qdrant port | No | `6333` |
| **Qdrant Cloud Mode** | | | |
| `QDRANT_URL` | Qdrant Cloud URL | Cloud only | - |
| `QDRANT_API_KEY` | Qdrant Cloud API key | Cloud only | - |

## 📚 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Main Endpoint

**POST** `/generate-tests`
```json
{
  "query": "Your test scenario description"
}
```

## 🏗️ Project Structure

```
├── 🚀 main.py                     # FastAPI server entry point
├── ⚙️ config.py                   # Configuration management  
├── 📄 file_ingestion.py           # Document processing (.docx)
├── 🔢 embedding.py                # Gemini embeddings
├── 🕸️ neo4j_graph.py              # Neo4j operations
├── 🔍 qdrant_vector.py            # Qdrant vector operations
├── 🔗 integrated_graphrag.py      # Hybrid system (Neo4j + Qdrant)
├── 🤖 agent.py                    # AI test generation
├── 📋 models.py                   # Pydantic data models
├── 💾 memory_graph.py             # Fallback in-memory system
├── 🐳 docker-compose.yml          # Qdrant Docker setup
├── 📦 requirements.txt            # Python dependencies
├── 📁 documents/                  # Your .docx files go here
└── 🎨 frontend/                   # React UI
    ├── package.json
    ├── public/
    └── src/
```

## 🚀 Deployment

### For Production

1. **Use environment variables** instead of `.env` file
2. **Set up proper Neo4j instance** (not free tier)
3. **Use persistent Qdrant storage**
4. **Build React for production**: `npm run build`
5. **Use production WSGI server**: `gunicorn main:app`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if needed
5. Submit a pull request

## � License

This project is licensed under the MIT License.

---

**🎉 Happy Testing!** If you run into any issues, please create an issue on GitHub.
