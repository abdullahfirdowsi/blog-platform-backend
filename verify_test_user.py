import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import get_database, connect_to_mongo, close_mongo_connection

async def verify_test_user():
    """Manually verify the test user's email in the database"""
    try:
        # Connect to database first
        await connect_to_mongo()
        
        db = await get_database()
        test_email = "testuser.profile@example.com"
        
        # Check if user exists
        user = await db.users.find_one({"email": test_email})
        if not user:
            print(f"❌ User with email {test_email} not found")
            return False
        
        print(f"📋 Found user: {user['username']} ({user['email']})")
        print(f"   Current verification status: {user.get('email_verified', False)}")
        
        # Update user to mark email as verified
        result = await db.users.update_one(
            {"email": test_email},
            {
                "$set": {"email_verified": True},
                "$unset": {
                    "email_verification_token": "",
                    "email_verification_token_expires": ""
                }
            }
        )
        
        if result.modified_count > 0:
            print(f"✅ Successfully verified email for {test_email}")
            return True
        else:
            print(f"⚠️ User {test_email} was already verified")
            return True
            
    except Exception as e:
        print(f"❌ Error verifying user: {str(e)}")
        return False
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(verify_test_user())

