#!/usr/bin/env python3
"""
Test script to check email validation error messages
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000/api/v1"

def test_email_validation():
    """Test different email validation scenarios"""
    
    print("🧪 Testing Email Validation Error Messages")
    print("==========================================\n")
    
    # Test cases for different email validation scenarios
    test_cases = [
        {
            "name": "Invalid email format - missing @",
            "data": {
                "username": "testuser1",
                "email": "invalid-email",
                "password": "password123"
            }
        },
        {
            "name": "Invalid email format - incomplete domain",
            "data": {
                "username": "testuser2",
                "email": "invalid@",
                "password": "password123"
            }
        },
        {
            "name": "Invalid email format - no domain",
            "data": {
                "username": "testuser3",
                "email": "user@",
                "password": "password123"
            }
        },
        {
            "name": "Valid email format (should pass validation, might fail on duplicate)",
            "data": {
                "username": "testuser4",
                "email": "test@example.com",
                "password": "password123"
            }
        },
        {
            "name": "Empty email",
            "data": {
                "username": "testuser5",
                "email": "",
                "password": "password123"
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"{i}. {test_case['name']}")
        print(f"   Input: {test_case['data']['email']}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/auth/register",
                json=test_case['data'],
                headers={"Content-Type": "application/json"}
            )
            
            print(f"   Status: {response.status_code}")
            
            if response.status_code in [400, 422]:
                try:
                    error_data = response.json()
                    if 'detail' in error_data:
                        print(f"   Error: {error_data['detail']}")
                    if 'errors' in error_data:
                        print(f"   Errors: {json.dumps(error_data['errors'], indent=8)}")
                except:
                    print(f"   Raw response: {response.text}")
            elif response.status_code == 200:
                success_data = response.json()
                print(f"   Success: {success_data.get('message', 'Registration successful')}")
            else:
                print(f"   Unexpected status: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("   ❌ Could not connect to server. Make sure the server is running on localhost:8000")
            return
        except Exception as e:
            print(f"   ❌ Error: {str(e)}")
        
        print()
    
    print("✅ Email validation testing completed!")
    print("\n📝 Notes:")
    print("- Invalid email formats should show user-friendly error messages")
    print("- Valid email that already exists should show 'Email already registered'")
    print("- Valid new email should succeed or show appropriate business logic errors")

if __name__ == "__main__":
    test_email_validation()

