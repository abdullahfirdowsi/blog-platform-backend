#!/usr/bin/env python3
"""
Direct test of Pydantic validation for email fields
"""

from pydantic import ValidationError
import json
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.models.models import UserCreate, UserLogin
from fastapi.exceptions import RequestValidationError
from fastapi import Request

def test_pydantic_validation():
    """Test Pydantic validation directly"""
    
    print("🧪 Testing Pydantic Email Validation")
    print("====================================\n")
    
    test_cases = [
        {
            "name": "Invalid email - missing @",
            "data": {"username": "test", "email": "invalid-email", "password": "password123"}
        },
        {
            "name": "Invalid email - incomplete domain", 
            "data": {"username": "test", "email": "invalid@", "password": "password123"}
        },
        {
            "name": "Empty email",
            "data": {"username": "test", "email": "", "password": "password123"}
        },
        {
            "name": "Valid email",
            "data": {"username": "test", "email": "test@example.com", "password": "password123"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Input: '{test_case['data']['email']}'")
        
        try:
            user = UserCreate(**test_case['data'])
            print(f"   ✅ Valid: {user.email}")
        except ValidationError as e:
            print(f"   ❌ Validation Error:")
            for error in e.errors():
                print(f"       Field: {error.get('loc', 'unknown')}")
                print(f"       Type: {error.get('type', 'unknown')}")
                print(f"       Message: {error.get('msg', 'no message')}")
        except Exception as e:
            print(f"   ❌ Other Error: {str(e)}")
        
        print()
    
    print("✅ Direct Pydantic validation testing completed!")

if __name__ == "__main__":
    test_pydantic_validation()

