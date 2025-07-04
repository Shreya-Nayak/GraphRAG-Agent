import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from file_ingestion import ingest_documents
from embedding import get_gemini_embedding, dummy_embedding
from integrated_graphrag import IntegratedGraphRAG  # Use Neo4j + Qdrant
from agent import generate_test_suite

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("🚀 FastAPI server starting...")
    print("📋 GraphRAG initialization will run in background...")
    # Start graph initialization in background without blocking server startup
    asyncio.create_task(initialize_graph())
    yield
    # Shutdown
    if global_graph:
        global_graph.close()

app = FastAPI(
    title="GraphRAG Test Generator", 
    description="AI-powered test case generation using Neo4j Aura DB and Qdrant vector database",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

doc_folder = "documents"

# Global integrated graph instance (Neo4j + Qdrant)
global_graph = None
graph_initialized = False

async def initialize_graph():
    """Initialize the integrated knowledge graph (Neo4j + Qdrant) from documents"""
    global graph_initialized, global_graph
    try:
        print("📂 Starting document ingestion for Neo4j + Qdrant...")
        
        # Initialize the integrated system
        try:
            global_graph = IntegratedGraphRAG()
            print("✅ Connected to Neo4j Aura DB + Qdrant Docker")
        except Exception as db_error:
            print(f"⚠️  External DB connection failed: {db_error}")
            print("🔄 Falling back to in-memory system...")
            from memory_graph import InMemoryGraphRAG
            global_graph = InMemoryGraphRAG()
        
        # Ingest and process all documents
        chunks = ingest_documents(doc_folder)
        print(f"📄 Found {len(chunks)} document chunks")
        
        if not chunks:
            print("⚠️  No document chunks found. Creating demo chunks for testing.")
            # Create some demo chunks for testing
            chunks = [
                {
                    "text": "User authentication should validate credentials and return appropriate responses for valid and invalid login attempts.",
                    "file_name": "demo_auth.docx",
                    "section_title": "Authentication Requirements",
                    "doc_type": "PRD"
                },
                {
                    "text": "Payment processing must handle various card types, validate amounts, and process transactions securely.",
                    "file_name": "demo_payment.docx", 
                    "section_title": "Payment Processing",
                    "doc_type": "HLD"
                },
                {
                    "text": "API endpoints should return proper HTTP status codes and error messages for different scenarios.",
                    "file_name": "demo_api.docx",
                    "section_title": "API Specifications", 
                    "doc_type": "API_SPEC"
                }
            ]
        
        # Generate embeddings for all chunks
        print("🧠 Starting embedding generation...")
        for i, chunk in enumerate(chunks):
            try:
                print(f"🔄 Processing chunk {i+1}/{len(chunks)}: {chunk['file_name']}")
                chunk["embedding"] = await get_gemini_embedding(chunk["text"])
            except Exception as e:
                print(f"⚠️  Embedding failed for chunk {i+1}, using fallback: {e}")
                chunk["embedding"] = dummy_embedding(chunk["text"])
        
        print("✅ Embedding generation completed")
        
        # Build integrated knowledge graph (Neo4j + Qdrant)
        print("🔗 Building integrated knowledge graph...")
        global_graph.create_chunk_nodes(chunks)
        global_graph.link_chunks(chunks)
        print("✅ Integrated knowledge graph construction completed")
        
        # Get system statistics
        stats = global_graph.get_system_stats()
        print(f"📊 System Stats: {stats}")
        
        graph_initialized = True
        print("🎉 GraphRAG system ready with Neo4j Aura DB + Qdrant!")
        
    except Exception as e:
        print(f"❌ Error in initialize_graph: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to previous system if initialization fails
        print("🔄 Falling back to in-memory system...")
        try:
            from memory_graph import InMemoryGraphRAG
            global_graph = InMemoryGraphRAG()
            
            # Process chunks with in-memory system
            chunks = ingest_documents(doc_folder)
            if chunks:
                for chunk in chunks[:10]:  # Limit for fallback
                    try:
                        chunk["embedding"] = await get_gemini_embedding(chunk["text"])
                    except:
                        chunk["embedding"] = dummy_embedding(chunk["text"])
                
                global_graph.create_chunk_nodes(chunks)
                global_graph.link_chunks(chunks)
                graph_initialized = True
                print("✅ Fallback in-memory system ready")
            
        except Exception as fallback_error:
            print(f"❌ Fallback also failed: {fallback_error}")
            global_graph = None
        traceback.print_exc()

# Remove the old startup event handler since we're using lifespan now

@app.get("/")
async def root():
    return {
        "message": "Welcome to GraphRAG Test Generator!",
        "docs": "/docs", 
        "health": "/health",
        "generate_tests": "/generate-tests"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint with detailed system status"""
    status = {
        "status": "healthy" if graph_initialized else "initializing",
        "graph_initialized": graph_initialized,
        "system_type": "Neo4j + Qdrant" if global_graph and hasattr(global_graph, 'neo4j_graph') else "In-Memory",
        "message": "GraphRAG API running with integrated Neo4j Aura DB + Qdrant vector database",
        "timestamp": "2025-01-04T00:00:00Z"
    }
    
    if global_graph and hasattr(global_graph, 'get_system_stats'):
        try:
            stats = global_graph.get_system_stats()
            status.update(stats)
        except Exception as e:
            status["stats_error"] = str(e)
    elif global_graph and hasattr(global_graph, 'get_collection_info'):
        # Fallback for in-memory system
        try:
            collection_info = global_graph.get_collection_info()
            status["fallback_info"] = collection_info
        except:
            pass
    
    return status

class QueryRequest(BaseModel):
    query: str

@app.post("/generate-tests")
async def generate_tests(req: QueryRequest):
    try:
        print(f"🔍 Processing query: {req.query}")
        
        if not graph_initialized:
            print("⚠️  Graph not yet initialized, generating multiple basic test cases")
            from models import TestCase, TestType, Priority, TestStep
            
            basic_tests = [
                TestCase(
                    title=f"Generic Test: {req.query}",
                    summary="High-level test case generated before graph initialization",
                    test_type=TestType.GENERIC,
                    priority=Priority.HIGH,
                    preconditions="System should be accessible and functional",
                    description=f"Validate the overall functionality and behavior of {req.query}. This test should cover the main use cases, user workflows, data validation, and ensure the feature works as expected under normal conditions.",
                    labels=["generic", "fallback", "initialization"],
                    steps=None,
                    expected_result=None,
                    test_script=None,
                    components=[]
                ),
                TestCase(
                    title=f"Functional Test: {req.query}",
                    summary="Basic functional validation",
                    test_type=TestType.FUNCTIONAL,
                    priority=Priority.MEDIUM,
                    preconditions="Test environment is set up",
                    description=None,
                    steps=[
                        TestStep(
                            action="Initialize test environment",
                            data="Basic test configuration",
                            expected_result="Environment is ready for testing"
                        ),
                        TestStep(
                            action="Execute the main functionality",
                            data=req.query,
                            expected_result="Functionality executes without errors"
                        ),
                        TestStep(
                            action="Verify expected outcomes",
                            data=None,
                            expected_result="Results match expected behavior"
                        )
                    ],
                    expected_result="Feature works correctly according to basic requirements",
                    test_script="# Basic functional test\ndef test_functionality():\n    setup_environment()\n    result = execute_functionality()\n    assert result.is_successful()",
                    labels=["functional", "basic"],
                    components=["core-system"]
                ),
                TestCase(
                    title=f"Error Handling: {req.query}",
                    summary="Basic error handling validation",
                    test_type=TestType.GENERIC,
                    priority=Priority.MEDIUM,
                    preconditions="System in normal state",
                    description=f"Test the system's ability to handle errors related to {req.query}. This should include testing with invalid inputs, checking error messages, and ensuring system stability after errors occur.",
                    labels=["error-handling", "generic", "basic"],
                    steps=None,
                    expected_result=None,
                    test_script=None,
                    components=[]
                )
            ]
            
            return {
                "query": req.query,
                "test_cases": [test.dict() for test in basic_tests],
                "total_count": len(basic_tests)
            }
        
        # Generate query embedding
        print("🧠 Generating query embedding...")
        try:
            query_embedding = await get_gemini_embedding(req.query)
        except Exception as e:
            print(f"⚠️  Query embedding failed, using fallback: {e}")
            query_embedding = dummy_embedding(req.query)
        
        # Search for relevant chunks in memory
        print("🔎 Searching for relevant document chunks in memory...")
        try:
            chunks = global_graph.get_relevant_chunks(query_embedding, top_k=5)
            print(f"📄 Found {len(chunks)} relevant chunks")
            
            if chunks:
                # Expand context using graph relationships
                chunk_ids = [c["chunk_id"] for c in chunks]
                expanded = global_graph.expand_context(chunk_ids, hops=2)
                context = "\n\n".join([f"Source: {c['file_name']}\nSection: {c.get('section_title', 'N/A')}\nContent: {c['text']}" for c in expanded])
                print(f"📖 Expanded context: {len(context)} characters from {len(expanded)} chunks")
            else:
                print("⚠️  No relevant chunks found, using query-based context")
                context = f"Query context: {req.query}\nNo specific document context found."
                
        except Exception as e:
            print(f"❌ Error during chunk retrieval: {e}")
            context = f"Query: {req.query}\nContext retrieval failed, generating based on query alone."
        
        # Generate test suite using AI
        print("🤖 Generating test cases with AI...")
        try:
            suite = await generate_test_suite(req.query, context)
            print(f"✅ Generated {len(suite.test_cases)} test cases")
            return suite.dict()
        except Exception as e:
            print(f"❌ Error generating test suite with AI: {e}")
            # Comprehensive fallback response with Jira Xray format
            from models import TestCase, TestType, Priority, TestStep
            
            fallback_tests = [
                TestCase(
                    title=f"Generic Test: {req.query}",
                    summary=f"High-level validation of {req.query}",
                    test_type=TestType.GENERIC,
                    priority=Priority.HIGH,
                    preconditions="System is accessible and user has required permissions",
                    description=f"Validate that {req.query} functions correctly according to business requirements. This test should cover the main functionality, user workflows, data validation, and system integration aspects. Ensure proper error handling and user experience.",
                    labels=["generic", "high-level"],
                    steps=None,
                    expected_result=None,
                    test_script=None,
                    components=[]
                ),
                TestCase(
                    title=f"Functional Test: {req.query}",
                    summary=f"Validates the main functionality of {req.query}",
                    test_type=TestType.FUNCTIONAL,
                    priority=Priority.HIGH,
                    preconditions="System is accessible and user has required permissions",
                    description=None,
                    steps=[
                        TestStep(
                            action="Set up test environment and data",
                            data="Test data configuration",
                            expected_result="Environment is properly configured"
                        ),
                        TestStep(
                            action="Navigate to the relevant feature/page",
                            data="Application URL or navigation path",
                            expected_result="Successfully navigated to target feature"
                        ),
                        TestStep(
                            action="Execute the primary test action",
                            data=req.query,
                            expected_result="Action completes successfully"
                        ),
                        TestStep(
                            action="Verify the main functionality",
                            data=None,
                            expected_result="Functionality works as expected"
                        )
                    ],
                    expected_result="The feature should work correctly according to requirements",
                    test_script="# Functional test script\ndef test_functionality():\n    # Setup\n    setup_test_environment()\n    \n    # Execute\n    result = execute_functionality()\n    \n    # Assert\n    assert result.is_successful()\n    assert result.meets_requirements()",
                    labels=["functional", "automated"],
                    components=["core-functionality"]
                ),
                TestCase(
                    title=f"Error Handling Test: {req.query}",
                    summary=f"Validates error handling and recovery for {req.query}",
                    test_type=TestType.GENERIC,
                    priority=Priority.MEDIUM,
                    preconditions="System in normal state, error scenarios prepared",
                    description=f"Test the system's ability to handle various error conditions related to {req.query}. This includes invalid inputs, system failures, network issues, and other edge cases. Verify that appropriate error messages are displayed and the system remains stable.",
                    labels=["error-handling", "negative-testing", "generic"],
                    steps=None,
                    expected_result=None,
                    test_script=None,
                    components=[]
                )
            ]
            
            return {
                "query": req.query,
                "test_cases": [test.dict() for test in fallback_tests],
                "total_count": len(fallback_tests)
            }
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting GraphRAG Test Generator with in-memory knowledge graph...")
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
