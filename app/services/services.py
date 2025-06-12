import os
import json
import re
import logging
from datetime import datetime
from typing import Optional

from fastapi import HTTPException
from motor.motor_asyncio import AsyncIOMotorDatabase
import google.generativeai as genai

from app.models.models import BlogSummaryResponse
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db

        # Configure Gemini AI
        api_key = getattr(settings, 'GEMINI_API_KEY', None) or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")

        genai.configure(api_key=api_key)

        model_name = getattr(settings, 'GEMINI_MODEL', None) or os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
        self.model = genai.GenerativeModel(model_name=model_name)

        self.generation_config = {
            "temperature": float(getattr(settings, 'GEMINI_TEMPERATURE', 0.7)),
            "top_p": float(getattr(settings, 'GEMINI_TOP_P', 0.8)),
            "top_k": int(getattr(settings, 'GEMINI_TOP_K', 40)),
            "max_output_tokens": int(getattr(settings, 'GEMINI_MAX_TOKENS', 150))
        }

    def extract_text_from_blog_content(self, content: str) -> str:
        """Extract plain text from structured blog content (JSON)"""
        try:
            content_data = json.loads(content)
            blocks = content_data.get('blocks', []) if isinstance(content_data, dict) else content_data if isinstance(content_data, list) else []

            text_parts = []
            for block in blocks:
                block_type = block.get('type', '')
                data = block.get('data', {})

                if block_type in ['content', 'subtitle']:
                    text = data if isinstance(data, str) else ''
                elif block_type in ['paragraph', 'header', 'quote']:
                    text = data.get('text', '')
                elif block_type == 'list':
                    items = data.get('items', [])
                    for item in items:
                        clean_item = re.sub(r'<[^>]+>', '', str(item)).strip()
                        if clean_item:
                            text_parts.append(clean_item)
                    continue
                else:
                    continue

                clean_text = re.sub(r'<[^>]+>', '', text).strip()
                if clean_text:
                    text_parts.append(clean_text)

            return ' '.join(text_parts).strip() or content.strip()

        except (json.JSONDecodeError, KeyError, TypeError) as e:
            logger.warning(f"Failed to parse blog content as JSON: {e}")
            return content.strip() if content else ""

    async def generate_summary(self, blog_content: str, blog_title: str) -> str:
        """Generate a short AI-powered summary using Gemini"""
        try:
            text_content = self.extract_text_from_blog_content(blog_content)
            max_content_length = 2000
            if len(text_content) > max_content_length:
                text_content = text_content[:max_content_length] + "..."

            prompt = f"""
Please provide a concise summary of the following blog post in 2-3 sentences.
Focus on the main points and key takeaways.

Title: {blog_title}

Content:
{text_content}

Summary:
"""

            response = self.model.generate_content(
                prompt,
                generation_config=self.generation_config
            )

            if response.text:
                return response.text.strip()

            raise HTTPException(status_code=500, detail="Empty response from AI")

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error generating AI summary: {str(e)}")

    async def create_blog_summary(self, blog_id: str, blog_content: str, blog_title: str) -> BlogSummaryResponse:
        """Create and return a new blog summary"""
        try:
            summary_text = await self.generate_summary(blog_content, blog_title)
            return BlogSummaryResponse(
                blog_id=blog_id,
                summary=summary_text,
                created_at=datetime.now()
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error creating blog summary: {str(e)}")

    async def get_blog_summary(self, blog_id: str) -> Optional[BlogSummaryResponse]:
        """Fetch blog summary from DB"""
        try:
            summary = await self.db.blog_summaries.find_one({"blog_id": blog_id})
            return BlogSummaryResponse(**summary) if summary else None
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error retrieving blog summary: {str(e)}")

    async def delete_blog_summary(self, blog_id: str) -> bool:
        """Delete a blog summary from DB"""
        try:
            result = await self.db.blog_summaries.delete_one({"blog_id": blog_id})
            return result.deleted_count > 0
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error deleting blog summary: {str(e)}")
