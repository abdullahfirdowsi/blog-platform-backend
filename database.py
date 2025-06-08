# In database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
import ssl
import certifi

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database() -> AsyncIOMotorClient:
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    try:
        # Standard connection options for MongoDB Atlas
        connection_options = {
            "serverSelectionTimeoutMS": 10000,
            "connectTimeoutMS": 10000,
            "socketTimeoutMS": 10000,
            "maxPoolSize": 10,
            "retryWrites": True,
            "w": "majority",
        }
        
        # Try connection with default SSL (which is required for MongoDB Atlas)
        try:
            db.client = AsyncIOMotorClient(settings.MONGODB_URL, **connection_options)
            db.database = db.client.get_database("blogging")
            await db.client.server_info()
            print("✅ Connected to MongoDB successfully")
            return
        except Exception as connection_error:
            error_msg = str(connection_error)
            
            # Provide specific guidance based on error type
            if "TLSV1_ALERT_INTERNAL_ERROR" in error_msg:
                print("❌ MongoDB SSL/TLS Error - This usually indicates:")
                print("   1. Your IP address is not whitelisted in MongoDB Atlas Network Access")
                print("   2. The MongoDB cluster has SSL/TLS configuration issues")
                print("   3. Corporate firewall is blocking the SSL handshake")
                print("\n🔧 To fix this:")
                print("   • Go to MongoDB Atlas Dashboard → Network Access → Add IP Address")
                print("   • Add your current IP or use 0.0.0.0/0 for development (not recommended for production)")
                print("   • Wait 2-3 minutes for changes to propagate")
            elif "connection closed" in error_msg:
                print("❌ MongoDB Connection Closed - Your IP is likely not whitelisted")
                print("\n🔧 Fix: Add your IP to MongoDB Atlas Network Access whitelist")
            elif "authentication failed" in error_msg.lower():
                print("❌ MongoDB Authentication Failed - Check your credentials")
            else:
                print(f"❌ MongoDB Connection Failed: {error_msg[:200]}...")
            
            print(f"\n📋 Connection URL being used: {settings.MONGODB_URL[:50]}...")
        
    except Exception as e:
        print(f"❌ MongoDB initialization error: {e}")
        
    # Set up a dummy database object so the app can still start
    print("⚠️  Starting application without MongoDB connection")
    print("   Some features requiring database access will not work")
    db.client = None
    db.database = None

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")