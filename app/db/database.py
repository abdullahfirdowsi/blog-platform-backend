from motor.motor_asyncio import AsyncIOMotorClient
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None

db = Database()

async def get_database() -> AsyncIOMotorClient:
    return db.database

async def connect_to_mongo():
    """Create database connection"""
    try:
        db.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
        db.database = db.client.get_database("blogging")  

        # Test the connection
        await db.client.server_info()
        logger.info("✅ Connected to MongoDB")
        
    except Exception as e:
        logger.exception("❌ Failed to connect to MongoDB")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        logger.info("🛑 Disconnected from MongoDB")
