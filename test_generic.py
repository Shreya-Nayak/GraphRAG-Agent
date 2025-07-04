#!/usr/bin/env python3
"""
Test the new generic test case functionality
"""

from models import TestCase, TestType, Priority

def test_generic_test_case():
    """Test creating a generic test case"""
    print("🔍 Testing generic test case creation...")
    
    try:
        # Create a generic test case
        generic_test = TestCase(
            title="Generic Login Validation",
            summary="High-level validation of login functionality",
            test_type=TestType.GENERIC,
            priority=Priority.HIGH,
            preconditions="User account exists in system",
            description="Validate that users can successfully log into the system using valid credentials. Test should cover various login scenarios including successful login, failed login with invalid credentials, account lockout scenarios, and password reset functionality. Ensure proper error handling and security measures are in place.",
            labels=["login", "authentication", "security"],
            steps=None,
            expected_result=None,
            test_script=None,
            components=[]
        )
        
        print("✅ Generic test case created successfully")
        print(f"Title: {generic_test.title}")
        print(f"Type: {generic_test.test_type}")
        print(f"Has steps: {generic_test.steps is not None}")
        print(f"Has description: {generic_test.description is not None}")
        print(f"Description length: {len(generic_test.description) if generic_test.description else 0} chars")
        
        # Create a functional test case for comparison
        functional_test = TestCase(
            title="Functional Login Test",
            summary="Detailed validation of login functionality",
            test_type=TestType.FUNCTIONAL,
            priority=Priority.HIGH,
            preconditions="User account exists in system",
            description=None,
            labels=["login", "functional"],
            steps=[],  # Would normally have TestStep objects
            expected_result="User successfully logs in",
            test_script="def test_login(): pass",
            components=["auth-service"]
        )
        
        print("✅ Functional test case created successfully")
        print(f"Functional has steps: {functional_test.steps is not None}")
        print(f"Functional has expected_result: {functional_test.expected_result is not None}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_generic_test_case()
    if success:
        print("\n🎉 Generic test case functionality working correctly!")
    else:
        print("\n❌ Generic test case functionality failed!")
