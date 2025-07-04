from typing import List, Optional, Union
from pydantic import BaseModel
from enum import Enum

class TestType(str, Enum):
    FUNCTIONAL = "functional"
    INTEGRATION = "integration"
    API = "api"
    UI = "ui"
    PERFORMANCE = "performance"
    SECURITY = "security"
    GENERIC = "generic"

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class TestStep(BaseModel):
    action: str
    data: Optional[Union[str, dict]] = None
    expected_result: str

class TestCase(BaseModel):
    title: str
    summary: str
    test_type: TestType
    priority: Priority
    preconditions: Optional[str] = None
    description: Optional[str] = None  # Unstructured definition for generic tests
    labels: List[str] = []
    
    # These fields are optional and used only for non-generic test types
    steps: Optional[List[TestStep]] = None
    expected_result: Optional[str] = None
    test_script: Optional[str] = None
    components: List[str] = []

class TestSuite(BaseModel):
    query: str
    test_cases: List[TestCase]
    total_count: int
