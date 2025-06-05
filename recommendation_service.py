from typing import List, Tuple, Optional
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from models import BlogResponse, BlogRecommendationResponse
from database import get_database
from bson import ObjectId

class BlogRecommendationService:
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that', 'the',
            'to', 'was', 'will', 'with', 'the', 'this', 'but', 'they', 'have',
            'had', 'what', 'said', 'each', 'which', 'she', 'do', 'how', 'their',
            'if', 'up', 'out', 'many', 'then', 'them', 'these', 'so', 'some',
            'her', 'would', 'make', 'like', 'into', 'him', 'time', 'two', 'more',
            'go', 'no', 'way', 'could', 'my', 'than', 'first', 'been', 'call',
            'who', 'oil', 'sit', 'now', 'find', 'down', 'day', 'did', 'get', 'come',
            'made', 'may', 'part'
        }
    
    def preprocess_text(self, text: str) -> str:
        """Clean and preprocess text for TF-IDF calculation"""
        if not text:
            return ""
        # Convert to lowercase
        text = text.lower()
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        # Split into words and remove stop words
        words = [word for word in text.split() if word not in self.stop_words and len(word) > 2]
        return ' '.join(words)
    
    def calculate_content_similarity(self, user_interests: List[str], blog_content: str, blog_title: str, blog_tags: List[str]) -> float:
        """Calculate similarity between user interests and blog content using TF-IDF"""
        if not user_interests:
            return 0.0
        
        # Combine user interests into a single document
        user_profile = ' '.join(user_interests)
        
        # Combine blog content, title, and tags (with different weights)
        blog_document = f"{blog_title} {blog_title} {blog_content} {' '.join(blog_tags)} {' '.join(blog_tags)}"
        
        # Preprocess both documents
        user_profile_clean = self.preprocess_text(user_profile)
        blog_document_clean = self.preprocess_text(blog_document)
        
        if not user_profile_clean or not blog_document_clean:
            return 0.0
        
        try:
            # Create TF-IDF vectorizer
            vectorizer = TfidfVectorizer(
                max_features=1000,
                ngram_range=(1, 2),  # Use unigrams and bigrams
                min_df=1,
                max_df=0.8
            )
            
            # Fit and transform documents
            documents = [user_profile_clean, blog_document_clean]
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            # Calculate cosine similarity
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
            
            return float(similarity)
        except:
            # Fallback to simple keyword matching if TF-IDF fails
            return self.simple_keyword_similarity(user_interests, blog_document_clean)
    
    def simple_keyword_similarity(self, user_interests: List[str], blog_content: str) -> float:
        """Fallback similarity calculation using keyword matching"""
        blog_words = set(blog_content.lower().split())
        interest_words = set(' '.join(user_interests).lower().split())
        
        if not interest_words:
            return 0.0
        
        intersection = blog_words.intersection(interest_words)
        return len(intersection) / len(interest_words)
    
    def calculate_engagement_score(self, blog: dict) -> float:
        """Calculate engagement score based on blog metadata"""
        # Base score
        score = 0.0
        
        # Recency bonus (newer posts get higher scores)
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        created_at = blog.get('created_at', now)
        
        if isinstance(created_at, datetime):
            days_old = (now - created_at).days
            if days_old < 1:
                score += 0.3
            elif days_old < 7:
                score += 0.2
            elif days_old < 30:
                score += 0.1
        
        # Published posts get priority
        if blog.get('published', False):
            score += 0.2
        
        return score
    
    async def get_all_blogs_sorted_by_interest(
        self, 
        user_interests: Optional[List[str]] = None, 
        page: int = 1, 
        page_size: int = 10,
        published_only: bool = True,
        tag_id: Optional[str] = None
    ) -> Tuple[List[BlogRecommendationResponse], int]:
        """Get ALL blogs but sorted by user interest relevance"""
        db = await get_database()
        
        # Build query filter
        query_filter = {}
        if published_only:
            query_filter["published"] = True
        if tag_id:
            query_filter["tag_ids"] = ObjectId(tag_id)
        
        # Get all blogs matching the filter
        cursor = db.blogs.find(query_filter)
        all_blogs = await cursor.to_list(length=None)
        
        # Get tag names for blogs
        tag_ids = set()
        for blog in all_blogs:
            tag_ids.update(blog.get('tag_ids', []))
        
        tag_names_map = {}
        if tag_ids:
            tags_cursor = db.tags.find({"_id": {"$in": list(tag_ids)}})
            tags = await tags_cursor.to_list(length=None)
            tag_names_map = {tag['_id']: tag['name'] for tag in tags}
        
        # Calculate recommendation scores for ALL blogs
        recommendations = []
        for blog in all_blogs:
            # Get tag names for this blog
            blog_tag_names = [tag_names_map.get(tag_id, '') for tag_id in blog.get('tag_ids', [])]
            
            if user_interests:
                # Calculate content similarity based on user interests
                content_score = self.calculate_content_similarity(
                    user_interests,
                    blog.get('content', ''),
                    blog.get('title', ''),
                    blog_tag_names
                )
                
                # Calculate engagement score
                engagement_score = self.calculate_engagement_score(blog)
                
                # Combined score (weighted towards content similarity)
                total_score = (content_score * 0.8) + (engagement_score * 0.2)
            else:
                # If no user interests, sort by engagement only (recency + published status)
                total_score = self.calculate_engagement_score(blog)
            
            # Create blog response with tag names and converted ObjectIds
            blog_response_data = {
                "_id": str(blog["_id"]),
                "user_id": str(blog["user_id"]),
                "title": blog.get("title", ""),
                "content": blog.get("content", ""),
                "tag_ids": [str(tag_id) for tag_id in blog.get("tag_ids", [])],
                "main_image_url": blog.get("main_image_url"),
                "published": blog.get("published", False),
                "created_at": blog.get("created_at"),
                "updated_at": blog.get("updated_at"),
                "tags": blog_tag_names
            }
            
            blog_response = BlogResponse(**blog_response_data)
            
            recommendations.append(BlogRecommendationResponse(
                blog=blog_response,
                relevance_score=total_score
            ))
        
        # Sort by relevance score (descending) - this ensures interest-based sorting
        recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
        
        # Apply pagination
        total_count = len(recommendations)
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_recommendations = recommendations[start_idx:end_idx]
        
        return paginated_recommendations, total_count

# Global instance
recommendation_service = BlogRecommendationService()

