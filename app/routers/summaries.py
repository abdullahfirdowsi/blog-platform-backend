from fastapi import APIRouter, Depends, HTTPException, status
from app.models.models import BlogSummaryCreate, BlogSummaryResponse
from app.db.database import get_database
from app.services.services import AIService

router = APIRouter(prefix="/summaries", tags=["Summaries"])


@router.post("/", response_model=BlogSummaryResponse, status_code=status.HTTP_201_CREATED)
async def generate_summary(
    data: BlogSummaryCreate,
    db=Depends(get_database)
):
    """
    Generate and return a blog summary using AI based on the blog content.
    """
    try:
        ai_service = AIService(db)
        return await ai_service.create_blog_summary(
            blog_id=data.blog_id,
            blog_title=data.blog_title,
            blog_content=data.blog_content
        )
    except Exception as e:
        # Customize this to capture specific errors (e.g., AIServiceError)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Summary generation failed: {str(e)}"
        )
