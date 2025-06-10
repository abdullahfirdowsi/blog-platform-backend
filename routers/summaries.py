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

@router.get("/{blog_id}", response_model=BlogSummaryResponse)
async def get_summary(blog_id: str, db=Depends(get_database)):
    ai_service = AIService(db)
    summary = await ai_service.get_blog_summary(blog_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary

@router.delete("/{blog_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_summary(blog_id: str, db=Depends(get_database)):
    ai_service = AIService(db)
    deleted = await ai_service.delete_blog_summary(blog_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Summary not found")
