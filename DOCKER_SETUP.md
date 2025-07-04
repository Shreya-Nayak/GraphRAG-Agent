# Docker Desktop Startup Guide

## Prerequisites
1. **Docker Desktop**: Make sure Docker Desktop is installed and running
2. **Python 3.8+**: Required for the application

## Quick Start

### 1. Start Docker Desktop
- Open Docker Desktop application
- Wait for it to fully start (Docker icon should be green/running)

### 2. Start Qdrant Container
```powershell
# Navigate to project directory
cd "c:\Users\SH40178929\Documents\GraphRAG Agent neo4j"

# Start Qdrant using Docker Compose
docker-compose up -d qdrant
```

### 3. Install Python Dependencies
```powershell
# Install dependencies
pip install -r requirements.txt
```

### 4. Verify Setup
```powershell
# Run verification script
python quick_verify.py
```

### 5. Start the Application
```powershell
# Start FastAPI backend
python -m uvicorn main:app --reload --port 8000

# In another terminal, start React frontend
cd frontend
npm install
npm start
```

## Verification Commands

### Check Docker is Running
```powershell
docker ps
```

### Check Qdrant Container
```powershell
docker ps | findstr qdrant
```

### Test Qdrant Connection
```powershell
curl http://localhost:6333/health
```

## Troubleshooting

### Docker Issues
- Make sure Docker Desktop is running
- Restart Docker Desktop if needed
- Check Docker Desktop settings

### Qdrant Issues
- Run: `docker-compose down && docker-compose up -d qdrant`
- Check logs: `docker-compose logs qdrant`

### Python Issues
- Use virtual environment: `python -m venv .venv && .venv\Scripts\activate`
- Update pip: `python -m pip install --upgrade pip`
