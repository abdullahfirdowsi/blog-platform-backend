from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List, Optional
from datetime import datetime
from models import BlogCreate, BlogUpdate, BlogResponse, BlogInDB, UserInDB
from auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/blogs", tags=["blogs"])

@router.post("/", response_model=BlogResponse)
async def create_blog(blog: BlogCreate, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    blog_dict = {
        "user_id": current_user.id,
        "title": blog.title,
        "content": blog.content,
        "tag_ids": blog.tag_ids or [],
        "main_image_url": blog.main_image_url,
        "published": blog.published,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.blogs.insert_one(blog_dict)
    blog_dict["_id"] = result.inserted_id
    
    return BlogResponse(**blog_dict)

@router.get("/", response_model=List[BlogResponse])
async def get_blogs(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    published_only: bool = Query(True),
    tag_id: Optional[str] = Query(None)
):
    db = await get_database()
    
    # Build query filter
    query_filter = {}
    if published_only:
        query_filter["published"] = True
    if tag_id:
        query_filter["tag_ids"] = ObjectId(tag_id)
    
    cursor = db.blogs.find(query_filter).skip(skip).limit(limit).sort("created_at", -1)
    blogs = await cursor.to_list(length=limit)
    
    return [BlogResponse(**blog) for blog in blogs]

@router.get("/my-blogs", response_model=List[BlogResponse])
async def get_my_blogs(
    current_user: UserInDB = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    db = await get_database()
    
    cursor = db.blogs.find({"user_id": current_user.id}).skip(skip).limit(limit).sort("created_at", -1)
    blogs = await cursor.to_list(length=limit)
    
    return [BlogResponse(**blog) for blog in blogs]

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
    
    # Check if blog exists and belongs to current user
    existing_blog = await db.blogs.find_one({"_id": ObjectId(blog_id), "user_id": current_user.id})
    if not existing_blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found or you don't have permission to edit it"
        )
    
    # Build update data
    update_data = {"updated_at": datetime.utcnow()}
    if blog_update.title is not None:
        update_data["title"] = blog_update.title
    if blog_update.content is not None:
        update_data["content"] = blog_update.content
    if blog_update.tag_ids is not None:
        update_data["tag_ids"] = blog_update.tag_ids
    if blog_update.main_image_url is not None:
        update_data["main_image_url"] = blog_update.main_image_url
    if blog_update.published is not None:
        update_data["published"] = blog_update.published
    
    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$set": update_data}
    )
    
    updated_blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    return BlogResponse(**updated_blog)

@router.delete("/{blog_id}")
async def delete_blog(blog_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    # Check if blog exists and belongs to current user
    existing_blog = await db.blogs.find_one({"_id": ObjectId(blog_id), "user_id": current_user.id})
    if not existing_blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found or you don't have permission to delete it"
        )
    
    # Delete associated comments, likes, and images
    await db.comments.delete_many({"blog_id": ObjectId(blog_id)})
    await db.likes.delete_many({"blog_id": ObjectId(blog_id)})
    await db.images.delete_many({"blog_id": ObjectId(blog_id)})
    
    # Delete the blog
    await db.blogs.delete_one({"_id": ObjectId(blog_id)})
    
    return {"message": "Blog deleted successfully"}

@router.get("/search/{query}", response_model=List[BlogResponse])
async def search_blogs(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100)
):
    db = await get_database()
    
    # Search in title and content
    search_filter = {
        "$and": [
            {"published": True},
            {
                "$or": [
                    {"title": {"$regex": query, "$options": "i"}},
                    {"content": {"$regex": query, "$options": "i"}}
                ]
            }
        ]
    }
    
    cursor = db.blogs.find(search_filter).skip(skip).limit(limit).sort("created_at", -1)
    blogs = await cursor.to_list(length=limit)
    
    return [BlogResponse(**blog) for blog in blogs]

