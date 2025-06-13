#!/usr/bin/env python3
"""
Test FastAPI validation handler
"""

import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.testclient import TestClient
import sys
import os

# Add the app directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main import app

def test_fastapi_validation():
    """Test FastAPI validation with our custom exception handler"""
    
    print("🧪 Testing FastAPI Email Validation Handler")
    print("============================================\n")
    
    client = TestClient(app)
    
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
            "name": "Valid email format (may fail on duplicate check)",
            "data": {"username": "test", "email": "test@example.com", "password": "password123"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Input: '{test_case['data']['email']}'")
        
        try:
            response = client.post("/api/v1/auth/register", json=test_case['data'])
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [400, 422]:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"   Error: {error_data['detail']}")
                if 'errors' in error_data:
                    print(f"   Detailed errors:")
                    for error in error_data['errors']:
                        print(f"     - {error.get('field', 'unknown')}: {error.get('message', 'no message')}")
            elif response.status_code == 200:
                success_data = response.json()
                print(f"   ✅ Success: {success_data.get('message', 'Registration successful')}")
            else:
                print(f"   Unexpected status: {response.text}")
                
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    print("✅ FastAPI validation testing completed!")

if __name__ == "__main__":
    test_fastapi_validation()

