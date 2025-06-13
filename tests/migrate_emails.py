import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

async def normalize_existing_emails():
    """Normalize all existing email addresses in the database to lowercase"""
    
    # Connect to the database
    client = AsyncIOMotorClient(settings.MONGODB_URL)
    db = client["blogging"]
    
    # Get all users
    users = await db.users.find({}).to_list(length=None)
    
    print(f"Found {len(users)} users to process...")
    
    updated_count = 0
    
    for user in users:
        original_email = user['email']
        normalized_email = original_email.lower().strip()
        
        # Only update if the email actually changed
        if original_email != normalized_email:
            # Check if there's already a user with the normalized email
            existing = await db.users.find_one({"email": normalized_email})
            
            if existing and str(existing['_id']) != str(user['_id']):
                print(f"WARNING: Cannot normalize {original_email} to {normalized_email} - email already exists for another user")
                print(f"  Original user ID: {user['_id']}")
                print(f"  Existing user ID: {existing['_id']}")
                continue
            
            # Update the user's email
            await db.users.update_one(
                {"_id": user['_id']},
                {"$set": {"email": normalized_email}}
            )
            
            print(f"Updated: {original_email} -> {normalized_email}")
            updated_count += 1
        else:
            print(f"No change needed: {original_email}")
    
    print(f"\nCompleted! Updated {updated_count} out of {len(users)} users.")
    
    # Close the connection
    client.close()

if __name__ == "__main__":
    print("Starting email normalization migration...")
    asyncio.run(normalize_existing_emails())
    print("Migration completed!")

