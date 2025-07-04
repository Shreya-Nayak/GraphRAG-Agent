# GraphRAG Test Generator - Windows Startup Script
# Run this script to start the entire system

Write-Host "🤖 GraphRAG Test Case Generator" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Host "❌ .env file not found!" -ForegroundColor Red
    Write-Host "📝 Please create .env file with your API keys" -ForegroundColor Yellow
    Write-Host "   See README.md for instructions" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ .env file found" -ForegroundColor Green

# Start Qdrant
Write-Host "🐳 Starting Qdrant database..." -ForegroundColor Blue
try {
    docker-compose up -d qdrant
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Qdrant started successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Qdrant failed to start" -ForegroundColor Yellow
    }
} catch {
    Write-Host "❌ Docker not found or failed to start Qdrant" -ForegroundColor Red
    Write-Host "💡 Make sure Docker Desktop is running" -ForegroundColor Yellow
}

# Install dependencies
Write-Host "📦 Installing Python dependencies..." -ForegroundColor Blue
try {
    pip install -r requirements.txt
    Write-Host "✅ Dependencies installed" -ForegroundColor Green
} catch {
    Write-Host "❌ Failed to install dependencies" -ForegroundColor Red
    exit 1
}

# Start backend
Write-Host ""
Write-Host "⚡ Starting FastAPI backend..." -ForegroundColor Blue
Write-Host "🌐 Backend will be available at: http://localhost:8000" -ForegroundColor Cyan
Write-Host "📚 API docs will be at: http://localhost:8000/docs" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 To start the frontend, open another PowerShell window and run:" -ForegroundColor Yellow
Write-Host "   cd frontend" -ForegroundColor White
Write-Host "   npm install" -ForegroundColor White  
Write-Host "   npm start" -ForegroundColor White
Write-Host ""
Write-Host "🔄 Starting server (press Ctrl+C to stop)..." -ForegroundColor Blue

# Start the server
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
