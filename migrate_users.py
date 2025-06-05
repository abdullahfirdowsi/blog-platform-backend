#!/usr/bin/env python3
"""
Migration script to add new fields to existing users in the database.
Run this once after updating the user models.
"""

import asyncio
from database import get_database, connect_to_mongo, close_mongo_connection
from datetime import datetime

async def migrate_users():
    """Add missing fields to existing users"""
    print("Starting user migration...")
    
    # Connect to MongoDB
    await connect_to_mongo()
    db = await get_database()
    
    # Find all users that don't have the new fields
    users_to_update = await db.users.find({
        "$or": [
            {"full_name": {"$exists": False}},
            {"bio": {"$exists": False}},
            {"is_active": {"$exists": False}},
            {"role": {"$exists": False}}
        ]
    }).to_list(None)
    
    print(f"Found {len(users_to_update)} users to update")
    
    update_count = 0
    for user in users_to_update:
        update_fields = {}
        
        # Add missing fields with default values
        if "full_name" not in user:
            update_fields["full_name"] = None
        if "bio" not in user:
            update_fields["bio"] = None
        if "is_active" not in user:
            update_fields["is_active"] = True
        if "role" not in user:
            update_fields["role"] = "user"
        
        if update_fields:
            await db.users.update_one(
                {"_id": user["_id"]},
                {"$set": update_fields}
            )
            update_count += 1
            print(f"Updated user: {user.get('email', user.get('username', 'unknown'))}")
    
    print(f"Migration completed. Updated {update_count} users.")

async def main():
    try:
        await migrate_users()
    except Exception as e:
        print(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())

