from fastapi import APIRouter, Depends, HTTPException, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from database import get_database
from models import BlogSummaryResponse
from services.ai_service import AIService
from auth import get_current_user
from bson import ObjectId
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(tags=["Blog Summaries"])


@router.post("/generate/{blog_id}", response_model=BlogSummaryResponse)
async def generate_blog_summary(
    blog_id: str,
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Generate AI summary for a specific blog post.
    Only available for published blogs.
    """
    try:
        # Validate blog_id format
        if not ObjectId.is_valid(blog_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid blog ID format"
            )
        
        # Get the blog post
        blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Check if blog is published
        if not blog.get("published", False):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="AI summaries are only available for published blogs"
            )
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Generate and store summary
        summary = await ai_service.create_blog_summary(
            blog_id=blog_id,
            blog_content=blog.get("content", ""),
            blog_title=blog.get("title", "")
        )
        
        logger.info(f"Generated AI summary for blog {blog_id}")
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating blog summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while generating summary"
        )


@router.get("/blog/{blog_id}", response_model=BlogSummaryResponse)
async def get_blog_summary(
    blog_id: str,
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Get existing AI summary for a specific blog post.
    Public endpoint - no authentication required.
    """
    try:
        # Validate blog_id format
        if not ObjectId.is_valid(blog_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid blog ID format"
            )
        
        # Check if blog exists and is published
        blog = await db.blogs.find_one({"_id": ObjectId(blog_id), "published": True})
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Published blog not found"
            )
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Get existing summary
        summary = await ai_service.get_blog_summary(blog_id)
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No AI summary found for this blog"
            )
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving blog summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while retrieving summary"
        )


@router.delete("/blog/{blog_id}")
async def delete_blog_summary(
    blog_id: str,
    current_user=Depends(get_current_user),
    db: AsyncIOMotorDatabase = Depends(get_database)
):
    """
    Delete AI summary for a specific blog post.
    Only the blog author or admin can delete summaries.
    """
    try:
        # Validate blog_id format
        if not ObjectId.is_valid(blog_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid blog ID format"
            )
        
        # Get the blog post to check ownership
        blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
        if not blog:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Blog not found"
            )
        
        # Check if user is the author or admin
        if blog.get("user_id") != current_user["_id"] and current_user.get("role") != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the blog author or admin can delete summaries"
            )
        
        # Initialize AI service
        ai_service = AIService(db)
        
        # Delete summary
        deleted = await ai_service.delete_blog_summary(blog_id)
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No AI summary found for this blog"
            )
        
        logger.info(f"Deleted AI summary for blog {blog_id}")
        return {"message": "AI summary deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting blog summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error while deleting summary"
        )

