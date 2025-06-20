from fastapi import APIRouter, HTTPException, Depends, Query
from typing import Dict, List, Optional
from datetime import datetime, timezone, timedelta
from bson import ObjectId
from collections import defaultdict, Counter

from app.models.models import UserInDB
from app.core.auth import get_current_user
from app.db.database import get_database

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


# Helper function to check if user is admin (you can modify this based on your admin logic)
def is_admin(user: UserInDB) -> bool:
    # For now, we'll check if the user has "admin" in their username
    # In a real application, you'd have a proper role system
    admin_emails = ["blogplatform.live@gmail.com"]
    return (
        "admin" in user.username.lower() or 
        user.email.endswith("@admin.com") or
        user.email.lower() in admin_emails
    )


@router.get("/totals")
async def get_dashboard_totals(current_user: UserInDB = Depends(get_current_user)):
    """
    Get total counts for users, posts, comments, and likes.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    total_users = await db.users.count_documents({})
    total_posts = await db.blogs.count_documents({})
    total_comments = await db.comments.count_documents({})
    total_likes = await db.likes.count_documents({})
    
    return {
        "total_users": total_users,
        "total_posts": total_posts,
        "total_comments": total_comments,
        "total_likes": total_likes
    }


@router.get("/posts-over-time")
async def get_posts_over_time(
    period: str = Query("week", description="Time period: day, week, month, year"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get post counts aggregated over time periods.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    # Define aggregation pipeline based on period
    if period == "day":
        group_format = {
            "year": {"$year": "$created_at"},
            "month": {"$month": "$created_at"},
            "day": {"$dayOfMonth": "$created_at"}
        }
        date_format = "%Y-%m-%d"
    elif period == "week":
        group_format = {
            "year": {"$year": "$created_at"},
            "week": {"$week": "$created_at"}
        }
        date_format = "%Y-W%U"
    elif period == "month":
        group_format = {
            "year": {"$year": "$created_at"},
            "month": {"$month": "$created_at"}
        }
        date_format = "%Y-%m"
    elif period == "year":
        group_format = {
            "year": {"$year": "$created_at"}
        }
        date_format = "%Y"
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Use: day, week, month, year")
    
    pipeline = [
        {
            "$group": {
                "_id": group_format,
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    
    result = await db.blogs.aggregate(pipeline).to_list(length=None)
    
    # Format the result
    formatted_result = []
    for item in result:
        if period == "day":
            date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
        elif period == "week":
            date_str = f"{item['_id']['year']}-W{item['_id']['week']:02d}"
        elif period == "month":
            date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}"
        else:  # year
            date_str = str(item['_id']['year'])
        
        formatted_result.append({
            "period": date_str,
            "count": item['count']
        })
    
    return formatted_result


@router.get("/posts-by-category")
async def get_posts_by_category(current_user: UserInDB = Depends(get_current_user)):
    """
    Get post counts grouped by tags/categories.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    pipeline = [
        {"$unwind": "$tags"},
        {
            "$group": {
                "_id": "$tags",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": 20  # Top 20 categories
        }
    ]
    
    result = await db.blogs.aggregate(pipeline).to_list(length=20)
    
    return [
        {
            "category": item['_id'],
            "count": item['count']
        }
        for item in result
    ]


@router.get("/top-tags")
async def get_top_tags(
    limit: int = Query(20, ge=1, le=50),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get the most popular tags with counts.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    pipeline = [
        {"$unwind": "$tags"},
        {
            "$group": {
                "_id": "$tags",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"count": -1}
        },
        {
            "$limit": limit
        }
    ]
    
    result = await db.blogs.aggregate(pipeline).to_list(length=limit)
    
    return [
        {
            "tag": item['_id'],
            "count": item['count']
        }
        for item in result
    ]


@router.get("/most-liked")
async def get_most_liked_posts(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get the most liked posts.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    cursor = db.blogs.find({}).sort("likes_count", -1).limit(limit)
    posts = await cursor.to_list(length=limit)
    
    result = []
    for post in posts:
        # Get author info
        author = await db.users.find_one(
            {"_id": post["user_id"]}, 
            {"username": 1}
        )
        
        result.append({
            "id": str(post["_id"]),
            "title": post["title"],
            "author": author["username"] if author else "Unknown",
            "likes_count": post.get("likes_count", 0),
            "created_at": post["created_at"]
        })
    
    return result


@router.get("/most-commented")
async def get_most_commented_posts(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get the most commented posts.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    cursor = db.blogs.find({}).sort("comment_count", -1).limit(limit)
    posts = await cursor.to_list(length=limit)
    
    result = []
    for post in posts:
        # Get author info
        author = await db.users.find_one(
            {"_id": post["user_id"]}, 
            {"username": 1}
        )
        
        result.append({
            "id": str(post["_id"]),
            "title": post["title"],
            "author": author["username"] if author else "Unknown",
            "comment_count": post.get("comment_count", 0),
            "created_at": post["created_at"]
        })
    
    return result


@router.get("/users-over-time")
async def get_users_over_time(
    period: str = Query("month", description="Time period: day, week, month, year"),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get user signup counts aggregated over time periods.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    # Define aggregation pipeline based on period
    if period == "day":
        group_format = {
            "year": {"$year": "$created_at"},
            "month": {"$month": "$created_at"},
            "day": {"$dayOfMonth": "$created_at"}
        }
    elif period == "week":
        group_format = {
            "year": {"$year": "$created_at"},
            "week": {"$week": "$created_at"}
        }
    elif period == "month":
        group_format = {
            "year": {"$year": "$created_at"},
            "month": {"$month": "$created_at"}
        }
    elif period == "year":
        group_format = {
            "year": {"$year": "$created_at"}
        }
    else:
        raise HTTPException(status_code=400, detail="Invalid period. Use: day, week, month, year")
    
    pipeline = [
        {
            "$group": {
                "_id": group_format,
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}
        }
    ]
    
    result = await db.users.aggregate(pipeline).to_list(length=None)
    
    # Format the result
    formatted_result = []
    for item in result:
        if period == "day":
            date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}-{item['_id']['day']:02d}"
        elif period == "week":
            date_str = f"{item['_id']['year']}-W{item['_id']['week']:02d}"
        elif period == "month":
            date_str = f"{item['_id']['year']}-{item['_id']['month']:02d}"
        else:  # year
            date_str = str(item['_id']['year'])
        
        formatted_result.append({
            "period": date_str,
            "count": item['count']
        })
    
    return formatted_result


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = Query(20, ge=1, le=100),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get recent activity feed (posts, comments, likes).
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    # Get recent posts
    recent_posts = await db.blogs.find({}).sort("created_at", -1).limit(limit // 2).to_list(length=limit // 2)
    
    # Get recent comments
    recent_comments = await db.comments.find({}).sort("created_at", -1).limit(limit // 2).to_list(length=limit // 2)
    
    activities = []
    
    # Add posts to activities
    for post in recent_posts:
        author = await db.users.find_one({"_id": post["user_id"]}, {"username": 1})
        activities.append({
            "type": "post",
            "id": str(post["_id"]),
            "title": post["title"],
            "user": author["username"] if author else "Unknown",
            "created_at": post["created_at"],
            "description": f"New post: {post['title']}"
        })
    
    # Add comments to activities
    for comment in recent_comments:
        author = await db.users.find_one({"_id": comment["user_id"]}, {"username": 1})
        blog = await db.blogs.find_one({"_id": comment["blog_id"]}, {"title": 1})
        activities.append({
            "type": "comment",
            "id": str(comment["_id"]),
            "user": author["username"] if author else "Unknown",
            "created_at": comment["created_at"],
            "description": f"Commented on: {blog['title'] if blog else 'Unknown post'}"
        })
    
    # Sort by created_at descending
    activities.sort(key=lambda x: x["created_at"], reverse=True)
    
    return activities[:limit]


@router.get("/top-contributors")
async def get_top_contributors(
    limit: int = Query(10, ge=1, le=50),
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Get top contributors based on post and comment count.
    """
    if not is_admin(current_user):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = await get_database()
    
    # Get post counts per user
    post_pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "post_count": {"$sum": 1}
            }
        }
    ]
    post_counts = await db.blogs.aggregate(post_pipeline).to_list(length=None)
    
    # Get comment counts per user
    comment_pipeline = [
        {
            "$group": {
                "_id": "$user_id",
                "comment_count": {"$sum": 1}
            }
        }
    ]
    comment_counts = await db.comments.aggregate(comment_pipeline).to_list(length=None)
    
    # Combine counts
    user_stats = defaultdict(lambda: {"post_count": 0, "comment_count": 0})
    
    for item in post_counts:
        user_stats[item["_id"]]["post_count"] = item["post_count"]
    
    for item in comment_counts:
        user_stats[item["_id"]]["comment_count"] = item["comment_count"]
    
    # Calculate total contribution score and get user info
    contributors = []
    for user_id, stats in user_stats.items():
        user = await db.users.find_one({"_id": user_id}, {"username": 1, "email": 1, "created_at": 1})
        if user:
            total_score = stats["post_count"] * 3 + stats["comment_count"]  # Posts worth 3x comments
            contributors.append({
                "user_id": str(user_id),
                "username": user["username"],
                "email": user["email"],
                "post_count": stats["post_count"],
                "comment_count": stats["comment_count"],
                "total_score": total_score,
                "joined_at": user["created_at"]
            })
    
    # Sort by total score and return top contributors
    contributors.sort(key=lambda x: x["total_score"], reverse=True)
    
    return contributors[:limit]

