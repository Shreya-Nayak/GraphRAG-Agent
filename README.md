# GraphRAG Test Case Generator

A complete GraphRAG-powered agent using Pydantic AI with Google Gemini API and Neo4j for intelligent test case generation from technical documents.

## 🚀 Quick Start

### Backend Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up Neo4j Vector Index:**
   Open Neo4j Browser and run:
   ```cypher
   CREATE VECTOR INDEX chunk_embedding_index IF NOT EXISTS
   FOR (c:Chunk) ON (c.embedding)
   OPTIONS {indexConfig: {`vector.dimensions`: 256, `vector.similarity_function`: 'cosine'}}
   ```

3. **Start the FastAPI backend:**
   ```bash
   uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory:**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

3. **Start the React development server:**
   ```bash
   npm start
   ```

4. **Open your browser to:**
   ```
   http://localhost:3000
   ```

## 📋 Usage

1. **Start both servers** (backend on port 8000, frontend on port 3000)
2. **Open the React UI** in your browser
3. **Enter a test query** like:
   - "Login API should handle invalid credentials"
   - "User registration flow with validation"
   - "Payment processing with different card types"
4. **Click "Generate Test Cases"** to get AI-generated test cases and scripts
5. **Copy test cases** using the copy button for easy integration

## 🔧 Configuration

### Environment Variables (.env)
```
NEO4J_URI=neo4j+s://ef1f1fe9.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=dLUC9V2MfZpjSHZnw627NE6PXlzwyqEUSy9gKxufbew
NEO4J_DATABASE=neo4j
GEMINI_API_KEY=AIzaSyAVUMhLloQkzqZVOVyWwFWyoUGndWK-fMA
```

## 📁 Project Structure

```
├── main.py                 # FastAPI server
├── config.py              # Configuration management
├── file_ingestion.py      # Document processing
├── embedding.py           # Gemini embeddings
├── graph_builder.py       # Neo4j graph operations
├── agent.py               # Pydantic AI agent
├── models.py              # Data models
├── requirements.txt       # Python dependencies
├── documents/             # .docx files for processing
└── frontend/              # React UI
    ├── package.json
    ├── public/
    └── src/
        ├── App.js         # Main React component
        ├── index.js       # React entry point
        └── index.css      # Styling
```

## 🎯 Features

- **Document Ingestion**: Processes .docx files (PRD, HLD, LLD, API specs)
- **Knowledge Graph**: Builds relationships between document chunks
- **Vector Search**: Finds relevant context using embeddings
- **AI Generation**: Creates structured test cases using Gemini AI
- **Modern UI**: React-based interface with copy functionality
- **Error Handling**: Robust error management throughout the pipeline

## 🛠 API Endpoints

### POST /generate-tests
Generate test cases for a given query.

**Request:**
```json
{
  "query": "Login API should handle invalid credentials"
}
```

**Response:**
```json
{
  "query": "Login API should handle invalid credentials",
  "test_cases": [
    {
      "title": "Test invalid username",
      "steps": [
        "Navigate to login page",
        "Enter invalid username",
        "Enter valid password",
        "Click login button"
      ],
      "expected_result": "Should display 'Invalid credentials' error message"
    }
  ]
}
```

## 🚨 Troubleshooting

1. **Backend fails to start**: Check Neo4j connection and ensure vector index is created
2. **Frontend can't connect**: Ensure backend is running on port 8000
3. **No test cases generated**: Check if documents are in the `documents/` folder
4. **Embedding errors**: Verify Gemini API key is valid and enabled

## 📚 Tech Stack

- **Backend**: FastAPI, Neo4j, Google Gemini API, Pydantic AI
- **Frontend**: React, Axios
- **Database**: Neo4j with vector indexing
- **AI**: Google Gemini for embeddings and text generation
