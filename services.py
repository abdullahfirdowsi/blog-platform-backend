import json
import re
import os
import logging
from typing import Optional
import google.generativeai as genai
from fastapi import HTTPException
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from models import BlogSummaryCreate, BlogSummaryResponse, BlogSummaryInDB
from bson import ObjectId
from config import settings
from models import BlogSummaryCreate, BlogSummaryInDB, BlogSummaryResponse
 
# Set up logging
logger = logging.getLogger(__name__)
 
class AIService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        # Configure Gemini AI
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(
            model_name=getattr(settings, 'GEMINI_MODEL', None) or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        )
        # Configure generation parameters
        self.generation_config = {
            "temperature": float(getattr(settings, 'GEMINI_TEMPERATURE', None) or os.getenv("GEMINI_TEMPERATURE", "0.7")),
            "top_p": float(getattr(settings, 'GEMINI_TOP_P', None) or os.getenv("GEMINI_TOP_P", "0.8")),
            "top_k": int(getattr(settings, 'GEMINI_TOP_K', None) or os.getenv("GEMINI_TOP_K", "40")),
            "max_output_tokens": int(getattr(settings, 'GEMINI_MAX_TOKENS', None) or os.getenv("GEMINI_MAX_TOKENS", "150"))
        }
    def extract_text_from_blog_content(self, content: str) -> str:
        """Extract plain text from blog content JSON blocks"""
        try:
            # Parse the JSON content
            content_data = json.loads(content)
            # Extract text from different block types
            text_parts = []
            # Handle both Editor.js format and frontend block format
            blocks = []
            if isinstance(content_data, dict) and 'blocks' in content_data:
                # Editor.js format: {"blocks": [...], "time": ..., "version": ...}
                blocks = content_data.get('blocks', [])
            elif isinstance(content_data, list):
                # Frontend format: directly an array of blocks
                blocks = content_data
            for block in blocks:
                block_type = block.get('type', '')
                # Handle frontend block format (type: 'content', 'subtitle', 'image')
                if block_type in ['content', 'subtitle']:
                    # Frontend format: {"type": "content", "data": "text content"}
                    text = block.get('data', '')
                    if text and isinstance(text, str):
                        # Remove HTML tags if present
                        clean_text = re.sub(r'<[^>]+>', '', text).strip()
                        if clean_text:
                            text_parts.append(clean_text)
                # Handle Editor.js format
                elif block_type == 'paragraph':
                    # Editor.js paragraph: {"type": "paragraph", "data": {"text": "..."}}
                    text = block.get('data', {}).get('text', '')
                    clean_text = re.sub(r'<[^>]+>', '', text).strip()
                    if clean_text:
                        text_parts.append(clean_text)
                elif block_type == 'header':
                    # Editor.js header: {"type": "header", "data": {"text": "...", "level": 2}}
                    text = block.get('data', {}).get('text', '')
                    clean_text = re.sub(r'<[^>]+>', '', text).strip()
                    if clean_text:
                        text_parts.append(clean_text)
                elif block_type == 'list':
                    # Editor.js list: {"type": "list", "data": {"items": [...]}}
                    items = block.get('data', {}).get('items', [])
                    for item in items:
                        clean_text = re.sub(r'<[^>]+>', '', str(item)).strip()
                        if clean_text:
                            text_parts.append(clean_text)
                elif block_type == 'quote':
                    # Editor.js quote: {"type": "quote", "data": {"text": "..."}}
                    text = block.get('data', {}).get('text', '')
                    clean_text = re.sub(r'<[^>]+>', '', text).strip()
                    if clean_text:
                        text_parts.append(clean_text)
            # Join all text parts
            full_text = ' '.join(text_parts).strip()
            return full_text if full_text else content
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # If JSON parsing fails, treat as plain text
            logger.warning(f"Failed to parse blog content as JSON: {e}")
            return content.strip() if content else ""
    async def generate_summary(self, blog_content: str, blog_title: str) -> str:
        """Generate AI summary using Google Gemini"""
        try:
            # Extract plain text from blog content
            text_content = self.extract_text_from_blog_content(blog_content)
            # Limit content length to avoid token limits
            max_content_length = 2000
            if len(text_content) > max_content_length:
                text_content = text_content[:max_content_length] + "..."
            # Create prompt for summarization
            prompt = f"""
Please provide a concise summary of the following blog post in 2-3 sentences.
Focus on the main points and key takeaways.
 
Title: {blog_title}
 
Content:
{text_content}
 
Summary:"""
            # Generate summary using Gemini
            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )
            if response.text:
                return response.text.strip()
            else:
                raise HTTPException(
                    status_code=500, 
                    detail="Failed to generate summary - empty response from AI"
                )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error generating AI summary: {str(e)}"
            )
    async def create_blog_summary(self, blog_id: str, blog_content: str, blog_title: str) -> BlogSummaryResponse:
        """Create and store a new blog summary"""
        try:
            # Generate AI summary
            summary_text = await self.generate_summary(blog_content, blog_title)
            # Create summary document
            summary_data = {
                "blog_id": blog_id,
                "summary": summary_text,
                "created_at": datetime.now()
            }
            # return to ui
            return BlogSummaryResponse(**summary_data)
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating blog summary: {str(e)}"
            )
    async def get_blog_summary(self, blog_id: str) -> Optional[BlogSummaryResponse]:
        """Retrieve existing blog summary"""
        try:
            summary = await self.db.blog_summaries.find_one({"blog_id": blog_id})
            if summary:
                return BlogSummaryResponse(**summary)
            return None
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error retrieving blog summary: {str(e)}"
            )
    async def delete_blog_summary(self, blog_id: str) -> bool:
        """Delete blog summary when blog is deleted"""
        try:
            result = await self.db.blog_summaries.delete_one({"blog_id": blog_id})
            return result.deleted_count > 0
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error deleting blog summary: {str(e)}"
            )
 