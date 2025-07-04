import httpx
from models import TestSuite, TestCase, TestType, Priority, TestStep
from config import GEMINI_API_KEY
from typing import List
import json
import re

GEMINI_CHAT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

async def generate_test_suite(query: str, context: str) -> TestSuite:
    prompt = f"""
    You are an expert test case designer. Using the provided context, generate comprehensive test cases for the user query.
    
    Generate AT LEAST 5-8 test cases covering different scenarios and test types:
    - Generic test cases (high-level, unstructured definitions)
    - Functional test cases (detailed steps)
    - Edge cases and boundary conditions
    - Error handling scenarios
    - Integration scenarios (if applicable)
    
    For GENERIC test cases, provide:
    1. A descriptive title
    2. A summary explaining what the test validates
    3. test_type: "generic"
    4. Priority (high, medium, low)
    5. Preconditions (if any)
    6. An unstructured description (what to test without specific steps)
    7. Relevant labels
    
    For NON-GENERIC test cases, provide:
    1. A descriptive title
    2. A summary explaining what the test validates
    3. test_type: functional|integration|api|ui|performance|security
    4. Priority (high, medium, low)
    5. Preconditions (if any)
    6. Detailed test steps with actions, data, and expected results
    7. Overall expected result
    8. Executable test script (when applicable)
    9. Relevant labels and components
    
    IMPORTANT: Return valid JSON without escape sequences. Use simple quotes and avoid special characters that need escaping.
    
    Return the result as a JSON object matching this exact schema:
    {{
        "query": "{query}",
        "test_cases": [
            {{
                "title": "Descriptive test case title",
                "summary": "Brief description of what this test validates",
                "test_type": "generic|functional|integration|api|ui|performance|security",
                "priority": "high|medium|low",
                "preconditions": "Setup requirements or null",
                "description": "Unstructured definition for generic tests or null",
                "labels": ["label1", "label2"],
                "steps": [
                    {{
                        "action": "Step description",
                        "data": "Input data as string or JSON object",
                        "expected_result": "What should happen"
                    }}
                ] or null for generic tests,
                "expected_result": "Overall expected outcome or null for generic tests",
                "test_script": "Executable script code or null",
                "components": ["component1", "component2"]
            }}
        ],
        "total_count": number_of_test_cases
    }}
    
    Context from documentation:
    {context}
    
    User Query: {query}
    
    Important: Generate a mix of generic and detailed test cases. Generic test cases should have description but no steps/expected_result.
    """
    
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(GEMINI_CHAT_URL, headers=headers, params=params, json=data)
        resp.raise_for_status()
        result = resp.json()
        
        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            print(f"🤖 Raw LLM Response: {text[:200]}...")
            
            # Clean the response - remove markdown code blocks if present
            text = text.strip()
            if text.startswith("```json"):
                text = text[7:]
            if text.startswith("```"):
                text = text[3:]
            if text.endswith("```"):
                text = text[:-3]
            
            # Extract JSON from the response
            start = text.find('{')
            end = text.rfind('}') + 1
            if start == -1 or end == 0:
                raise ValueError("No JSON found in response")
                
            json_str = text[start:end]
            print(f"📄 Extracted JSON: {json_str[:300]}...")
            
            # Try to fix common JSON escape issues
            try:
                parsed_data = json.loads(json_str)
            except json.JSONDecodeError as json_error:
                print(f"⚠️  JSON decode error: {json_error}")
                print("🔧 Attempting to fix JSON escape issues...")
                
                # Fix common escape sequence issues
                fixed_json = json_str.replace('\\{', '{').replace('\\}', '}').replace('\\"', '"')
                # Fix escaped backslashes in paths
                import re
                fixed_json = re.sub(r'\\\\([^"\\])', r'\\\1', fixed_json)
                
                try:
                    parsed_data = json.loads(fixed_json)
                    print("✅ Fixed JSON parsing issues")
                except json.JSONDecodeError as second_error:
                    print(f"❌ Still cannot parse JSON: {second_error}")
                    # Try one more fix - remove problematic escape sequences
                    very_fixed_json = re.sub(r'\\[^"\\nrtbf/]', '', fixed_json)
                    parsed_data = json.loads(very_fixed_json)
                    print("✅ Applied aggressive JSON fixes")
            
            # Ensure we have the total_count field
            if "total_count" not in parsed_data:
                parsed_data["total_count"] = len(parsed_data.get("test_cases", []))
            
            obj = TestSuite(**parsed_data)
            print(f"✅ Generated {len(obj.test_cases)} test cases")
            return obj
            
        except Exception as e:
            print(f"❌ Error parsing LLM response: {e}")
            print(f"🔍 Raw response: {result}")
            
            # Fallback: Create multiple basic test cases
            fallback_tests = [
                TestCase(
                    title=f"Generic Test Case for: {query}",
                    summary="Basic test case generated as fallback",
                    test_type=TestType.GENERIC,
                    priority=Priority.MEDIUM,
                    preconditions=None,
                    description=f"Validate the functionality described in the query: {query}. This is a high-level test case that should be refined with specific test scenarios and validation criteria based on the requirements.",
                    labels=["automated", "fallback", "generic"],
                    steps=None,
                    expected_result=None,
                    test_script=None,
                    components=[]
                ),
                TestCase(
                    title=f"Functional Test: {query}",
                    summary="Basic functional validation",
                    test_type=TestType.FUNCTIONAL,
                    priority=Priority.HIGH,
                    preconditions="System is accessible",
                    description=None,
                    labels=["functional", "fallback"],
                    steps=[
                        TestStep(
                            action="Initialize test environment",
                            data="Basic test setup",
                            expected_result="Environment ready"
                        ),
                        TestStep(
                            action="Execute main functionality",
                            data=query,
                            expected_result="Functionality works as expected"
                        )
                    ],
                    expected_result="Feature functions correctly",
                    test_script="# Basic test\ndef test_functionality():\n    assert True",
                    components=["core"]
                ),
                TestCase(
                    title=f"Error Handling: {query}",
                    summary="Basic error handling validation",
                    test_type=TestType.GENERIC,
                    priority=Priority.MEDIUM,
                    preconditions="System in normal state",
                    description=f"Test error handling for {query}. Verify system handles invalid inputs and error conditions gracefully.",
                    labels=["error-handling", "fallback"],
                    steps=None,
                    expected_result=None,
                    test_script=None,
                    components=[]
                ),
                TestCase(
                    title=f"Integration Test: {query}",
                    summary="Basic integration testing",
                    test_type=TestType.INTEGRATION,
                    priority=Priority.MEDIUM,
                    preconditions="All components available",
                    description=None,
                    labels=["integration", "fallback"],
                    steps=[
                        TestStep(
                            action="Test component integration",
                            data=query,
                            expected_result="Components work together"
                        )
                    ],
                    expected_result="Integration functions correctly",
                    test_script=None,
                    components=["integration"]
                ),
                TestCase(
                    title=f"Security Test: {query}",
                    summary="Basic security validation",
                    test_type=TestType.SECURITY,
                    priority=Priority.MEDIUM,
                    preconditions="Security testing environment",
                    description=f"Validate security aspects of {query}. Check for vulnerabilities and security compliance.",
                    labels=["security", "fallback"],
                    steps=None,
                    expected_result=None,
                    test_script=None,
                    components=[]
                )
            ]
            
            return TestSuite(
                query=query,
                test_cases=fallback_tests,
                total_count=len(fallback_tests)
            )
