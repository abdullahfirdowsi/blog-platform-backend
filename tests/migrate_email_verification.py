#!/usr/bin/env python3
"""
Database migration script to add email verification fields to existing users.
This script adds email_verified, email_verification_token, and email_verification_token_expires
fields to existing user documents.

Usage: python migrate_email_verification.py
"""

import asyncio
import os
import sys
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from decouple import config

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import settings

async def migrate_users():
    """Add email verification fields to existing users"""
    print("🔄 Starting email verification migration...")
    
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.get_default_database()
    users_collection = db.users
    
    try:
        # Find all users that don't have email verification fields
        users_without_fields = await users_collection.count_documents({
            "email_verified": {"$exists": False}
        })
        
        print(f"📊 Found {users_without_fields} users to migrate")
        
        if users_without_fields == 0:
            print("✅ No users need migration. All users already have email verification fields.")
            return
        
        # Update all users without email verification fields
        result = await users_collection.update_many(
            {"email_verified": {"$exists": False}},
            {
                "$set": {
                    "email_verified": False,  # Set to False for existing users (they need to verify)
                    "email_verification_token": None,
                    "email_verification_token_expires": None
                }
            }
        )
        
        print(f"✅ Successfully migrated {result.modified_count} users")
        print("📧 Existing users will need to verify their email addresses")
        
        # Optional: You can uncomment this to mark all existing users as verified
        # if you don't want to force them to verify their emails
        """
        await users_collection.update_many(
            {"email_verified": False},
            {"$set": {"email_verified": True}}
        )
        print("🔓 Marked all existing users as email verified")
        """
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        raise
    
    finally:
        # Close the connection
        client.close()
        print("🔌 Database connection closed")

async def verify_migration():
    """Verify that the migration was successful"""
    print("\n🔍 Verifying migration...")
    
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client.get_default_database()
    users_collection = db.users
    
    try:
        # Count users with email verification fields
        total_users = await users_collection.count_documents({})
        users_with_fields = await users_collection.count_documents({
            "email_verified": {"$exists": True}
        })
        verified_users = await users_collection.count_documents({
            "email_verified": True
        })
        unverified_users = await users_collection.count_documents({
            "email_verified": False
        })
        
        print(f"📊 Migration Results:")
        print(f"   Total users: {total_users}")
        print(f"   Users with email verification fields: {users_with_fields}")
        print(f"   Verified users: {verified_users}")
        print(f"   Unverified users: {unverified_users}")
        
        if users_with_fields == total_users:
            print("✅ Migration successful! All users have email verification fields.")
        else:
            print("⚠️  Some users may not have been migrated properly.")
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
    
    finally:
        client.close()

def main():
    """Main function to run the migration"""
    print("🚀 Email Verification Migration Script")
    print("=====================================\n")
    
    # Check if we can connect to the database
    try:
        # Run the migration
        asyncio.run(migrate_users())
        
        # Verify the migration
        asyncio.run(verify_migration())
        
        print("\n🎉 Migration completed successfully!")
        print("\n📝 Next steps:")
        print("   1. Restart your FastAPI server")
        print("   2. Test user registration with email verification")
        print("   3. Existing users will need to verify their emails before logging in")
        print("   4. Use the /auth/resend-verification endpoint for existing users")
        
    except Exception as e:
        print(f"\n💥 Migration failed with error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()

