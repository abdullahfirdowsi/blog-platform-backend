import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from ..core.config import settings
from ..db.database import get_database
import logging

logger = logging.getLogger(__name__)

class PasswordResetService:
    def __init__(self):
        self.token_expire_minutes = settings.RESET_TOKEN_EXPIRE_MINUTES
    
    async def get_users_collection(self):
        db = await get_database()
        return db.users

    def generate_reset_token(self) -> str:
        """
        Generate a secure random token for password reset
        """
        return secrets.token_urlsafe(32)

    def hash_token(self, token: str) -> str:
        """
        Hash the token for secure storage
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_reset_token(self, email: str) -> Optional[str]:
        """
        Create and store a password reset token for the user
        """
        try:
            users_collection = await self.get_users_collection()
            # Check if user exists
            user = await users_collection.find_one({"email": email})
            if not user:
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return None

            # Generate token
            token = self.generate_reset_token()
            hashed_token = self.hash_token(token)
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
            
            # Store hashed token in user document
            await users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "reset_token": hashed_token,
                        "reset_token_expires": expires_at
                    }
                }
            )
            
            logger.info(f"Password reset token created for user: {email}")
            return token  # Return unhashed token for email
            
        except Exception as e:
            logger.error(f"Error creating reset token for {email}: {str(e)}")
            return None

    async def validate_reset_token(self, token: str) -> Optional[str]:
        """
        Validate reset token and return the user's email if valid
        """
        try:
            users_collection = await self.get_users_collection()
            hashed_token = self.hash_token(token)
            
            # Find user with this token
            user = await users_collection.find_one({
                "reset_token": hashed_token,
                "reset_token_expires": {"$gt": datetime.utcnow()}
            })
            
            if not user:
                logger.warning("Invalid or expired reset token used")
                return None
                
            return user["email"]
            
        except Exception as e:
            logger.error(f"Error validating reset token: {str(e)}")
            return None

    async def clear_reset_token(self, email: str) -> bool:
        """
        Clear the reset token after successful password reset
        """
        try:
            users_collection = await self.get_users_collection()
            result = await users_collection.update_one(
                {"email": email},
                {
                    "$unset": {
                        "reset_token": "",
                        "reset_token_expires": ""
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Reset token cleared for user: {email}")
                return True
            else:
                logger.warning(f"No reset token found to clear for user: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing reset token for {email}: {str(e)}")
            return False

    async def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired reset tokens from the database
        """
        try:
            users_collection = await self.get_users_collection()
            result = await users_collection.update_many(
                {"reset_token_expires": {"$lt": datetime.utcnow()}},
                {
                    "$unset": {
                        "reset_token": "",
                        "reset_token_expires": ""
                    }
                }
            )
            
            logger.info(f"Cleaned up {result.modified_count} expired reset tokens")
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired tokens: {str(e)}")
            return 0

# Create a global instance
password_reset_service = PasswordResetService()

# Standalone functions for backward compatibility with auth router
async def generate_reset_token(user_id: str) -> Optional[str]:
    """
    Generate a reset token for the given user ID
    Note: This expects user_id (ObjectId) but we need to get the email first
    """
    from bson import ObjectId
    try:
        db = await get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return None
        return await password_reset_service.create_reset_token(user["email"])
    except Exception as e:
        logger.error(f"Error generating reset token for user {user_id}: {str(e)}")
        return None

async def validate_reset_token(token: str) -> Optional[str]:
    """
    Validate reset token and return the user ID if valid
    Note: This returns user_id instead of email to match auth router expectations
    """
    try:
        email = await password_reset_service.validate_reset_token(token)
        if not email:
            return None
        # Get user ID from email
        db = await get_database()
        user = await db.users.find_one({"email": email})
        if user:
            return str(user["_id"])
        return None
    except Exception as e:
        logger.error(f"Error validating reset token: {str(e)}")
        return None

async def clear_reset_token(user_id: str) -> bool:
    """
    Clear reset token for the given user ID
    """
    from bson import ObjectId
    try:
        db = await get_database()
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        if not user:
            return False
        return await password_reset_service.clear_reset_token(user["email"])
    except Exception as e:
        logger.error(f"Error clearing reset token for user {user_id}: {str(e)}")
        return False

