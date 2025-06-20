import secrets
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from ..core.config import settings
from ..db.database import get_database
import logging

logger = logging.getLogger(__name__)

class EmailVerificationService:
    def __init__(self):
        self.token_expire_minutes = settings.EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES
    
    async def get_users_collection(self):
        db = await get_database()
        return db.users

    def generate_verification_token(self) -> str:
        """
        Generate a secure random token for email verification
        """
        return secrets.token_urlsafe(32)

    def hash_token(self, token: str) -> str:
        """
        Hash the token for secure storage
        """
        return hashlib.sha256(token.encode()).hexdigest()

    async def create_verification_token(self, email: str) -> Optional[str]:
        """
        Create and store an email verification token for the user
        """
        try:
            users_collection = await self.get_users_collection()
            # Check if user exists
            user = await users_collection.find_one({"email": email})
            if not user:
                logger.warning(f"Email verification requested for non-existent email: {email}")
                return None

            # Generate token
            token = self.generate_verification_token()
            hashed_token = self.hash_token(token)
            
            # Calculate expiration time
            expires_at = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
            
            # Store hashed token in user document
            await users_collection.update_one(
                {"email": email},
                {
                    "$set": {
                        "email_verification_token": hashed_token,
                        "email_verification_token_expires": expires_at
                    }
                }
            )
            
            logger.info(f"Email verification token created for user: {email}")
            return token  # Return unhashed token for email
            
        except Exception as e:
            logger.error(f"Error creating verification token for {email}: {str(e)}")
            return None

    async def verify_email_token(self, token: str) -> Optional[str]:
        """
        Verify email token and return the user's email if valid
        """
        try:
            users_collection = await self.get_users_collection()
            hashed_token = self.hash_token(token)
            
            # Find user with this token
            user = await users_collection.find_one({
                "email_verification_token": hashed_token,
                "email_verification_token_expires": {"$gt": datetime.utcnow()}
            })
            
            if not user:
                logger.warning("Invalid or expired email verification token used")
                return None
                
            # Mark email as verified and clear token
            await users_collection.update_one(
                {"email": user["email"]},
                {
                    "$set": {"email_verified": True},
                    "$unset": {
                        "email_verification_token": "",
                        "email_verification_token_expires": ""
                    }
                }
            )
            
            logger.info(f"Email verified successfully for user: {user['email']}")
            return user["email"]
            
        except Exception as e:
            logger.error(f"Error verifying email token: {str(e)}")
            return None

    async def is_email_verified(self, email: str) -> bool:
        """
        Check if email is verified
        """
        try:
            users_collection = await self.get_users_collection()
            user = await users_collection.find_one({"email": email})
            return user.get("email_verified", False) if user else False
        except Exception as e:
            logger.error(f"Error checking email verification status for {email}: {str(e)}")
            return False

    async def clear_verification_token(self, email: str) -> bool:
        """
        Clear the verification token
        """
        try:
            users_collection = await self.get_users_collection()
            result = await users_collection.update_one(
                {"email": email},
                {
                    "$unset": {
                        "email_verification_token": "",
                        "email_verification_token_expires": ""
                    }
                }
            )
            
            if result.modified_count > 0:
                logger.info(f"Verification token cleared for user: {email}")
                return True
            else:
                logger.warning(f"No verification token found to clear for user: {email}")
                return False
                
        except Exception as e:
            logger.error(f"Error clearing verification token for {email}: {str(e)}")
            return False

    async def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired verification tokens from the database
        """
        try:
            users_collection = await self.get_users_collection()
            result = await users_collection.update_many(
                {"email_verification_token_expires": {"$lt": datetime.utcnow()}},
                {
                    "$unset": {
                        "email_verification_token": "",
                        "email_verification_token_expires": ""
                    }
                }
            )
            
            logger.info(f"Cleaned up {result.modified_count} expired verification tokens")
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired verification tokens: {str(e)}")
            return 0

# Create a global instance
email_verification_service = EmailVerificationService()

