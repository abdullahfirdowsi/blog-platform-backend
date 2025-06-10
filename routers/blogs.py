import re
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone
from models import (
    BlogCreate, BlogUpdate, BlogResponse, UserInDB,
    PaginatedBlogsResponse, BlogRecommendationResponse
)
from auth import get_current_user, get_current_user_optional
from database import get_database
from bson import ObjectId
from recommendation_service import recommendation_service

router = APIRouter(prefix="/blogs", tags=["blogs"])

@router.post("/", response_model=BlogResponse)
async def create_blog(blog: BlogCreate, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    # Process tags (remove empty/whitespace tags)
    if blog.tags:
        blog.tags = [tag.strip().lower() for tag in blog.tags if tag.strip()]
        
        # Check/create tags in the tags collection
        if blog.tags:
            # Build case-insensitive query for existing tags
            existing_tags = await db.tags.find({
                "$or": [
                    {"name": {"$regex": f"^{re.escape(tag)}$", "$options": "i"}} 
                    for tag in blog.tags
                ]
            }).to_list(None)
            
            existing_tag_names = {tag["name"].lower() for tag in existing_tags}
            
            # Insert new tags
            tags_to_insert = [
                {"name": tag, "created_at": datetime.now(timezone.utc)}
                for tag in blog.tags 
                if tag.lower() not in existing_tag_names
            ]
            
            if tags_to_insert:
                await db.tags.insert_many(tags_to_insert)
        
    blog_dict = {
        "user_id": ObjectId(current_user.id),
        "title": blog.title,
        "content": blog.content,
        "tags": blog.tags,
        "main_image_url": blog.main_image_url,
        "published": blog.published,
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "comment_count": 0,
        "likes_count": 0
    }
    
    result = await db.blogs.insert_one(blog_dict)
    
    # Convert ObjectIds to strings for the response
    blog_dict["_id"] = str(result.inserted_id)
    blog_dict["user_id"] = str(blog_dict["user_id"])
    
    return BlogResponse(**blog_dict)

@router.get("/", response_model=PaginatedBlogsResponse)
async def get_blogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    published_only: bool = Query(True),
    tags: Optional[str] = Query(None),
    current_user: Optional[UserInDB] = Depends(get_current_user_optional)
):
    """Get all blogs sorted by user interest relevance (if user is authenticated)"""
    
    # Get user interests if user is authenticated
    user_interests = None
    if current_user:
        db = await get_database()
        user_interests_doc = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
        if user_interests_doc:
            user_interests = user_interests_doc.get('interests', [])
            print(f"user_interest = {user_interests}")
    
    # Get blogs sorted by interest relevance
    recommendations, total_count = await recommendation_service.get_all_blogs_sorted_by_interest(
        user_interests=user_interests,
        page=page,
        page_size=page_size,
        published_only=published_only,
        tags=tags
    )
    
    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size
    
    # Extract just the blog data from recommendations
    blog_list = [rec.blog for rec in recommendations]
    
    return PaginatedBlogsResponse(
        blogs=blog_list,
        total=total_count,
        page=page,
        limit=page_size,
        total_pages=total_pages
    )

@router.get("/my-blogs", response_model=List[BlogResponse])
async def get_my_blogs(
    current_user: UserInDB = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    db = await get_database()
    
    # Calculate skip value from page    
    cursor = db.blogs.find({"user_id": ObjectId(current_user.id)}) \
         .sort("created_at", -1) \
         .skip((page - 1) * page_size) \
         .limit(page_size)
    blogs = await cursor.to_list(length=page_size)
    
    # Add tag names to blog responses
    blog_responses = []
    for blog in blogs:
        blog_response_data = {
            "_id": str(blog["_id"]),
            "user_id": str(blog["user_id"]),
            "title": blog.get("title", ""),
            "content": blog.get("content", ""),
            "tags": blog.get("tags", []),
            "main_image_url": blog.get("main_image_url"),
            "published": blog.get("published", False),
            "created_at": blog.get("created_at"),
            "updated_at": blog.get("updated_at"),
            "comment_count": blog.get("comment_count", 0),
            "likes_count": blog.get("likes_count", 0)
        }
        
        blog_response = BlogResponse(**blog_response_data)
        blog_responses.append(blog_response)
    
    return blog_responses

@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    # Convert ObjectIds to strings for the response
    blog["_id"] = str(blog["_id"])
    blog["user_id"] = str(blog["user_id"])
    
    return BlogResponse(**blog)

@router.put("/{blog_id}", response_model=BlogResponse)
async def update_blog(
    blog_id: str,
    blog_update: BlogUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    # First check if blog exists
    existing_blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not existing_blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    # Then check if user owns the blog
    if str(existing_blog["user_id"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to edit this blog"
        )
    
    # Build update data
    update_data = {"updated_at": datetime.now()}
    if blog_update.title is not None:
        update_data["title"] = blog_update.title
    if blog_update.content is not None:
        update_data["content"] = blog_update.content
    if blog_update.tags is not None:
        update_data["tags"] = blog_update.tags
    if blog_update.main_image_url is not None:
        update_data["main_image_url"] = blog_update.main_image_url
    if blog_update.published is not None:
        update_data["published"] = blog_update.published
    
    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": update_data}
    )
    
    updated_blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    
    # Convert ObjectIds to strings for the response
    updated_blog["_id"] = str(updated_blog["_id"])
    updated_blog["user_id"] = str(updated_blog["user_id"])
    updated_blog["tags"] = updated_blog.get("tags", [])
    
    return BlogResponse(**updated_blog)

@router.delete("/{blog_id}")
async def delete_blog(blog_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    # First check if blog exists
    existing_blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not existing_blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    # Then check if user owns the blog
    if str(existing_blog["user_id"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to delete this blog"
        )
    
    # Delete associated comments, likes
    await db.comments.delete_many({"blog_id": ObjectId(blog_id)})
    await db.likes.delete_many({"blog_id": ObjectId(blog_id)})
    
    # Delete the blog
    await db.blogs.delete_one({"_id": ObjectId(blog_id)})
    
    return {"message": "Blog deleted successfully"}

@router.get("/search/{query}", response_model=PaginatedBlogsResponse)
async def search_blogs(
    query: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: Optional[UserInDB] = Depends(get_current_user_optional)
):
    """Search blogs and sort by relevance to user interests"""
    db = await get_database()
    
    # Search in title and content
    search_filter = {
        "$and": [
            {"published": True},
            {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}},
                    {"tags": {"$regex": query, "$options": "i"}}
                ]
            }
        ]
    }
    
    cursor = db.blogs.find(search_filter)
    print(f"search_filter = {search_filter}")
    all_matching_blogs = await cursor.to_list(length=None)
    
    # Get user interests if user is authenticated
    user_interests = None
    if current_user:
        user_interests_doc = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
        if user_interests_doc:
            user_interests = user_interests_doc.get('interests', [])
    
    # Calculate relevance scores and sort
    recommendations = []
    for blog in all_matching_blogs:
        blog_tag_names = blog.get('tags', [])
        
        author = await db.users.find_one({"_id": blog["user_id"]})
        username = author.get("username") if author else "Unknown"
        
        if user_interests:
            # Calculate similarity score
            content_score = recommendation_service.calculate_content_similarity(
                user_interests,
                blog.get('content', ''),
                blog.get('title', ''),
                blog_tag_names
            )
            engagement_score = recommendation_service.calculate_engagement_score(blog)
            total_score = (content_score * 0.8) + (engagement_score * 0.2)
        else:
            # Sort by engagement only
            total_score = recommendation_service.calculate_engagement_score(blog)
        
        blog_response_data = {
            "_id": str(blog["_id"]),
            "user_id": str(blog["user_id"]),
            "title": blog.get("title", ""),
            "content": blog.get("content", ""),
            "tags": blog_tag_names,  # Directly use the tags
            "main_image_url": blog.get("main_image_url"),
            "published": blog.get("published", False),
            "created_at": blog.get("created_at"),
            "updated_at": blog.get("updated_at"),
            "comment_count": blog.get("comment_count", 0),
            "likes_count": blog.get("likes_count", 0),
            "username": username
        }
        
        blog_response = BlogResponse(**blog_response_data)
        recommendations.append(BlogRecommendationResponse(
            blog=blog_response,
            relevance_score=total_score
        ))
    
    # Sort by relevance
    recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # Apply pagination
    total_count = len(recommendations)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_recommendations = recommendations[start_idx:end_idx]
    
    total_pages = (total_count + page_size - 1) // page_size
    
    return PaginatedBlogsResponse(
        blogs=[rec.blog for rec in paginated_recommendations],
        total=total_count,
        page=page,
        limit=page_size,
        total_pages=total_pages
    )

