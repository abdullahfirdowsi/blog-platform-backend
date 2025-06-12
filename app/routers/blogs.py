from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from datetime import datetime, timezone
from bson import ObjectId

from app.models.models import (
    BlogCreate, BlogUpdate, BlogResponse, UserInDB,
    PaginatedBlogsResponse, BlogRecommendationResponse
)
from app.core.auth import get_current_user, get_current_user_optional
from app.db.database import get_database
from app.services.recommendation_service import recommendation_service

import re

router = APIRouter(prefix="/blogs", tags=["blogs"])


@router.post("/", response_model=BlogResponse)
async def create_blog(blog: BlogCreate, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()

    blog.tags = [tag.strip().lower() for tag in blog.tags or [] if tag.strip()]

    if blog.tags:
        existing_tags = await db.tags.find({
            "$or": [{"name": {"$regex": f"^{re.escape(tag)}$", "$options": "i"}} for tag in blog.tags]
        }).to_list(None)

        existing_tag_names = {tag["name"].lower() for tag in existing_tags}
        new_tags = [
            {"name": tag, "created_at": datetime.now(timezone.utc)}
            for tag in blog.tags if tag.lower() not in existing_tag_names
        ]
        if new_tags:
            await db.tags.insert_many(new_tags)

    blog_dict = {
        "user_id": ObjectId(current_user.id),
        "title": blog.title,
        "username":current_user.email,
        "content": blog.content,
        "tags": blog.tags,
        "main_image_url": blog.main_image_url,
        "published": blog.published,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "comment_count": 0,
        "likes_count": 0
    }

    result = await db.blogs.insert_one(blog_dict)
    blog_dict["_id"] = str(result.inserted_id)
    blog_dict["user_id"] = str(blog_dict["user_id"])

    return BlogResponse(**blog_dict)

def convert_objectid_to_str(document: dict):
    for key, value in document.items():
        if isinstance(value, ObjectId):
            document[key] = str(value)
    return document

@router.get("/", response_model=PaginatedBlogsResponse)
async def get_blogs(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    published_only: bool = Query(True),
    tags: Optional[str] = Query(None)
):
    db = await get_database()

    filters = {}
    if published_only:
        filters["published"] = True

    if tags:
        tag_list = [tag.strip() for tag in tags.split(",")]
        filters["tags"] = {"$in": tag_list}

    skip = (page - 1) * page_size
    total = await db.blogs.count_documents(filters)

    blogs_cursor = db.blogs.find(filters)\
        .sort("created_at", -1)\
        .skip(skip)\
        .limit(page_size)

    blogs = await blogs_cursor.to_list(length=page_size)

    # Add username to each blog
    for blog in blogs:
        blog = convert_objectid_to_str(blog)
        user = await db.users.find_one({"_id": ObjectId(blog["user_id"])}, {"username": 1})
        blog["username"] = user["username"] if user else "Unknown"

    return PaginatedBlogsResponse(
        blogs=blogs,
        total=total,
        page=page,
        limit=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.get("/my-blogs", response_model=List[BlogResponse])
async def get_my_blogs(
    current_user: UserInDB = Depends(get_current_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    db = await get_database()
    cursor = db.blogs.find(
        {"user_id": ObjectId(current_user.id)}
    ).sort("created_at", -1).skip((page - 1) * page_size).limit(page_size)

    blogs = await cursor.to_list(length=page_size)

    return [
        BlogResponse(
            _id=str(blog["_id"]),
            user_id=str(blog["user_id"]),
            username=current_user.username,  # Inject username here
            title=blog.get("title", ""),
            content=blog.get("content", ""),
            tags=blog.get("tags", []),
            main_image_url=blog.get("main_image_url"),
            published=blog.get("published", False),
            created_at=blog.get("created_at"),
            updated_at=blog.get("updated_at"),
            comment_count=blog.get("comment_count", 0),
            likes_count=blog.get("likes_count", 0)
        )
        for blog in blogs
    ]


@router.get("/{blog_id}", response_model=BlogResponse)
async def get_blog(blog_id: str):
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    # Convert ObjectIds to string
    blog["_id"] = str(blog["_id"])
    blog["user_id"] = str(blog["user_id"])

    # Fetch author's username
    author = await db.users.find_one({"_id": ObjectId(blog["user_id"])}, {"username": 1})
    blog["username"] = author["username"] if author else "Unknown"

    return BlogResponse(**blog)


@router.put("/{blog_id}", response_model=BlogResponse)
async def update_blog(
    blog_id: str,
    blog_update: BlogUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if str(blog["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to edit this blog")

    tags = [tag.strip().lower() for tag in blog_update.tags or [] if tag.strip()]

    if tags:
        existing_tags = await db.tags.find({
            "$or": [{"name": {"$regex": f"^{re.escape(tag)}$", "$options": "i"}} for tag in tags]
        }).to_list(None)

        existing_tag_names = {tag["name"].lower() for tag in existing_tags}
        new_tags = [
            {"name": tag, "created_at": datetime.now(timezone.utc)}
            for tag in tags if tag.lower() not in existing_tag_names
        ]
        if new_tags:
            await db.tags.insert_many(new_tags)

    update_data = {
        "updated_at": datetime.now(timezone.utc),
        **{k: v for k, v in blog_update.dict(exclude_unset=True).items()}
    }

    await db.blogs.update_one({"_id": ObjectId(blog_id)}, {"$set": update_data})
    updated_blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})

    updated_blog["_id"] = str(updated_blog["_id"])
    updated_blog["user_id"] = str(updated_blog["user_id"])

    return BlogResponse(**updated_blog)



@router.delete("/{blog_id}")
async def delete_blog(blog_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    if str(blog["user_id"]) != current_user.id:
        raise HTTPException(status_code=403, detail="You don't have permission to delete this blog")

    await db.comments.delete_many({"blog_id": ObjectId(blog_id)})
    await db.likes.delete_many({"blog_id": ObjectId(blog_id)})
    await db.blogs.delete_one({"_id": ObjectId(blog_id)})

    return {"message": "Blog deleted successfully"}


@router.get("/search/{query}", response_model=PaginatedBlogsResponse)
async def search_blogs(
    query: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    current_user: Optional[UserInDB] = Depends(get_current_user_optional)
):
    db = await get_database()

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

    blogs = await db.blogs.find(search_filter).to_list(length=None)

    user_interests = []
    if current_user:
        interests_doc = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
        user_interests = interests_doc.get("interests", []) if interests_doc else []

    recommendations = []
    for blog in blogs:
        author = await db.users.find_one({"_id": blog["user_id"]})
        username = author.get("username") if author else "Unknown"

        content_score = recommendation_service.calculate_content_similarity(
            user_interests, blog.get('content', ''), blog.get('title', ''), blog.get('tags', [])
        ) if user_interests else 0

        engagement_score = recommendation_service.calculate_engagement_score(blog)
        total_score = (content_score * 0.8 + engagement_score * 0.2) if user_interests else engagement_score

        recommendations.append(
            BlogRecommendationResponse(
                blog=BlogResponse(
                    _id=str(blog["_id"]),
                    user_id=str(blog["user_id"]),
                    username=username,
                    title=blog.get("title", ""),
                    content=blog.get("content", ""),
                    tags=blog.get("tags", []),
                    main_image_url=blog.get("main_image_url"),
                    published=blog.get("published", False),
                    created_at=blog.get("created_at"),
                    updated_at=blog.get("updated_at"),
                    comment_count=blog.get("comment_count", 0),
                    likes_count=blog.get("likes_count", 0),
                ),
                relevance_score=total_score
            )
        )

    recommendations.sort(key=lambda r: r.relevance_score, reverse=True)
    total_count = len(recommendations)
    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size

    return PaginatedBlogsResponse(
        blogs=[rec.blog for rec in recommendations[start_idx:end_idx]],
        total=total_count,
        page=page,
        limit=page_size,
        total_pages=(total_count + page_size - 1) // page_size
    )
