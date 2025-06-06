from fastapi import APIRouter, HTTPException, status, Depends, Query, Request
from typing import List, Optional
from datetime import datetime
from models import (
    BlogCreate, BlogUpdate, BlogResponse, BlogInDB, UserInDB,
    PaginatedBlogsResponse, BlogRecommendationResponse
)
from auth import get_current_user, get_current_user_optional
from database import get_database
from bson import ObjectId
from recommendation_service import recommendation_service

router = APIRouter(prefix="/blogs", tags=["blogs"])

@router.post("/debug", status_code=200)
async def debug_blog_data(request: Request):
    body = await request.body()
    headers = dict(request.headers)
    print(f"DEBUG RAW BODY: {body}")
    print(f"DEBUG HEADERS: {headers}")
    try:
        import json
        parsed_body = json.loads(body)
        print(f"DEBUG PARSED BODY: {parsed_body}")
        return {"message": "Debug successful", "body": parsed_body}
    except Exception as e:
        print(f"DEBUG ERROR: {e}")
        return {"message": "Debug error", "error": str(e)}

@router.post("/", response_model=BlogResponse)
async def create_blog(blog: BlogCreate, current_user: UserInDB = Depends(get_current_user)):
    print(f"DEBUG: Received blog data: {blog}")
    print(f"DEBUG: Blog content: {blog.content}")
    print(f"DEBUG: Blog tag_ids: {blog.tag_ids}")
    db = await get_database()
    
    # Convert tag_ids to ObjectIds
    tag_ids = []
    if blog.tag_ids:
        tag_ids = [ObjectId(tag_id) for tag_id in blog.tag_ids if ObjectId.is_valid(tag_id)]
    
    blog_dict = {
        "user_id": ObjectId(current_user.id),
        "title": blog.title,
        "blog_body": blog.content or "",  # Map frontend 'content' to backend 'blog_body', default to empty string
        "tag_ids": tag_ids,
        "main_image_url": blog.main_image_url,
        "published": blog.published,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.blogs.insert_one(blog_dict)
    
    # Convert ObjectIds to strings for the response
    blog_dict["id"] = str(result.inserted_id)
    blog_dict["user_id"] = str(blog_dict["user_id"])
    blog_dict["tag_ids"] = [str(tag_id) for tag_id in blog_dict["tag_ids"]]
    
    return BlogResponse(**blog_dict)

@router.get("/", response_model=PaginatedBlogsResponse)
async def get_blogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    published_only: bool = Query(True),
    tag_id: Optional[str] = Query(None),
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
    
    # Get blogs sorted by interest relevance
    recommendations, total_count = await recommendation_service.get_all_blogs_sorted_by_interest(
        user_interests=user_interests,
        page=page,
        page_size=page_size,
        published_only=published_only,
        tag_id=tag_id
    )
    
    # Calculate total pages
    total_pages = (total_count + page_size - 1) // page_size
    
    return PaginatedBlogsResponse(
        blogs=recommendations,
        total_count=total_count,
        page=page,
        page_size=page_size,
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
    skip = (page - 1) * page_size
    
    cursor = db.blogs.find({"user_id": ObjectId(current_user.id)}).skip(skip).limit(page_size).sort("created_at", -1)
    blogs = await cursor.to_list(length=page_size)
    
    # Get tag names for blogs
    tag_ids = set()
    for blog in blogs:
        tag_ids.update(blog.get('tag_ids', []))
    
    tag_names_map = {}
    if tag_ids:
        tags_cursor = db.tags.find({"_id": {"$in": list(tag_ids)}})
        tags = await tags_cursor.to_list(length=None)
        tag_names_map = {tag['_id']: tag['name'] for tag in tags}
    
    # Add tag names to blog responses
    blog_responses = []
    for blog in blogs:
        # Convert ObjectIds to strings
        blog_id_str = str(blog["_id"])
        user_id_str = str(blog["user_id"])
        tag_ids_str = [str(tag_id) for tag_id in blog.get("tag_ids", [])]
        
        # Get tag names using original ObjectIds
        blog_tag_names = [tag_names_map.get(tag_id, '') for tag_id in blog.get('tag_ids', [])]
        
        # Create response with converted IDs
        blog_response_data = {
            "id": blog_id_str,
            "user_id": user_id_str,
            "title": blog.get("title", ""),
            "blog_body": blog.get("blog_body", ""),
            "tag_ids": tag_ids_str,
            "main_image_url": blog.get("main_image_url"),
            "published": blog.get("published", False),
            "created_at": blog.get("created_at"),
            "updated_at": blog.get("updated_at"),
            "tags": blog_tag_names
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
    blog["id"] = str(blog["_id"])
    del blog["_id"]
    blog["user_id"] = str(blog["user_id"])
    blog["tag_ids"] = [str(tag_id) for tag_id in blog.get("tag_ids", [])]
    
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
    update_data = {"updated_at": datetime.utcnow()}
    if blog_update.title is not None:
        update_data["title"] = blog_update.title
    if blog_update.content is not None:
        update_data["blog_body"] = blog_update.content
    if blog_update.tag_ids is not None:
        # Convert tag_ids to ObjectIds
        tag_ids = [ObjectId(tag_id) for tag_id in blog_update.tag_ids if ObjectId.is_valid(tag_id)]
        update_data["tag_ids"] = tag_ids
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
    updated_blog["id"] = str(updated_blog["_id"])
    del updated_blog["_id"]
    updated_blog["user_id"] = str(updated_blog["user_id"])
    updated_blog["tag_ids"] = [str(tag_id) for tag_id in updated_blog.get("tag_ids", [])]
    
    # Get tag names for the response
    tag_ids = updated_blog.get("tag_ids", [])
    tag_names = []
    if tag_ids:
        # Convert string IDs back to ObjectIds for database query
        object_tag_ids = [ObjectId(tag_id) for tag_id in tag_ids if ObjectId.is_valid(tag_id)]
        if object_tag_ids:
            tags_cursor = db.tags.find({"_id": {"$in": object_tag_ids}})
            tags = await tags_cursor.to_list(length=None)
            tag_names = [tag['name'] for tag in tags]
    
    updated_blog["tags"] = tag_names
    
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
    
    # Delete associated comments, likes, and images
    await db.comments.delete_many({"blog_id": ObjectId(blog_id)})
    await db.likes.delete_many({"blog_id": ObjectId(blog_id)})
    await db.images.delete_many({"blog_id": ObjectId(blog_id)})
    
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
    
    # Search in title and blog_body
    search_filter = {
        "$and": [
            {"published": True},
            {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"blog_body": {"$regex": query, "$options": "i"}}
                ]
            }
        ]
    }
    
    cursor = db.blogs.find(search_filter)
    all_matching_blogs = await cursor.to_list(length=None)
    
    # Get user interests if user is authenticated
    user_interests = None
    if current_user:
        user_interests_doc = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
        if user_interests_doc:
            user_interests = user_interests_doc.get('interests', [])
    
    # Get tag names for blogs
    tag_ids = set()
    for blog in all_matching_blogs:
        tag_ids.update(blog.get('tag_ids', []))
    
    tag_names_map = {}
    if tag_ids:
        tags_cursor = db.tags.find({"_id": {"$in": list(tag_ids)}})
        tags = await tags_cursor.to_list(length=None)
        tag_names_map = {tag['_id']: tag['name'] for tag in tags}
    
    # Calculate relevance scores and sort
    recommendations = []
    for blog in all_matching_blogs:
        blog_tag_names = [tag_names_map.get(tag_id, '') for tag_id in blog.get('tag_ids', [])]
        
        if user_interests:
            # Calculate similarity score
            content_score = recommendation_service.calculate_content_similarity(
                user_interests,
                blog.get('blog_body', ''),
                blog.get('title', ''),
                blog_tag_names
            )
            engagement_score = recommendation_service.calculate_engagement_score(blog)
            total_score = (content_score * 0.8) + (engagement_score * 0.2)
        else:
            # Sort by engagement only
            total_score = recommendation_service.calculate_engagement_score(blog)
        
        # Convert ObjectIds to strings for response
        blog_response_data = {
            "id": str(blog["_id"]),
            "user_id": str(blog["user_id"]),
            "title": blog.get("title", ""),
            "blog_body": blog.get("blog_body", ""),
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
    
    # Sort by relevance
    recommendations.sort(key=lambda x: x.relevance_score, reverse=True)
    
    # Apply pagination
    total_count = len(recommendations)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_recommendations = recommendations[start_idx:end_idx]
    
    total_pages = (total_count + page_size - 1) // page_size
    
    return PaginatedBlogsResponse(
        blogs=paginated_recommendations,
        total_count=total_count,
        page=page,
        page_size=page_size,
        total_pages=total_pages
    )

