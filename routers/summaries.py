from fastapi import APIRouter, Depends
from fastapi import HTTPException, status
from models import BlogSummaryCreate, BlogSummaryResponse
from database import get_database
from services  import AIService
from models import BlogSummaryCreate, BlogSummaryInDB, BlogSummaryResponse

router = APIRouter(prefix="/summaries", tags=["Summaries"])

@router.post("/", response_model=BlogSummaryResponse)
async def generate_summary(data: BlogSummaryCreate, db=Depends(get_database)):
    ai_service = AIService(db)
    return await ai_service.create_blog_summary(
        blog_id=data.blog_id,
        blog_title=data.blog_title,
        blog_content=data.blog_content
    )
