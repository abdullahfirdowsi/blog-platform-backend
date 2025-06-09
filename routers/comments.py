from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from datetime import datetime, timezone
from models import CommentCreate, CommentResponse, UserInDB
from auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/comments", tags=["comments"])

@router.post("/blogs/{blog_id}", response_model=CommentResponse)
async def create_comment(
    blog_id: str,
    comment: CommentCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    # Check if blog exists
    blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    comment_dict = {
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id),
        "user_name": current_user.username,
        "text": comment.text,
        "created_at": datetime.now(timezone.utc),
        "updated_at": None  # Initially, no updates
    }
    
    result = await db.comments.insert_one(comment_dict)
    
    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"comment_count": 1}}
    )
    
    comment_dict["_id"] = str(result.inserted_id)
    comment_dict["blog_id"] = str(comment_dict["blog_id"])
    comment_dict["user_id"] = str(comment_dict["user_id"])
    comment_dict["user_name"] = str(comment_dict["user_name"])
    
    return CommentResponse(**comment_dict)

@router.get("/blogs/{blog_id}", response_model=List[CommentResponse])
async def get_blog_comments(
    blog_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    cursor = db.comments.find({"blog_id": ObjectId(blog_id)}).skip(skip).limit(limit).sort("created_at", -1)
    comments = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings for each comment
    for comment in comments:
        comment["_id"] = str(comment["_id"])
        comment["blog_id"] = str(comment["blog_id"])
        comment["user_id"] = str(comment["user_id"])
    
    return [CommentResponse(**comment) for comment in comments]

@router.get("/my-comments", response_model=List[CommentResponse])
async def get_my_comments(
    current_user: UserInDB = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    db = await get_database()
    
    cursor = db.comments.find({"user_id": ObjectId(current_user.id)}).skip(skip).limit(limit).sort("created_at", -1)
    comments = await cursor.to_list(length=limit)
    
    # Convert ObjectIds to strings for each comment
    for comment in comments:
        comment["_id"] = str(comment["_id"])
        comment["blog_id"] = str(comment["blog_id"])
        comment["user_id"] = str(comment["user_id"])
    
    return [CommentResponse(**comment) for comment in comments]

@router.put("/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: str,
    comment_update: CommentCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment ID"
        )
    
    # Check if comment exists and belongs to current user
    existing_comment = await db.comments.find_one({
        "_id": ObjectId(comment_id),
        "user_id": ObjectId(current_user.id)  # Ensures ownership
    })
    
    if not existing_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to edit it"
        )
    
    # Prepare update with new timestamp
    update_data = {
        "text": comment_update.text,
        "updated_at": datetime.now(timezone.utc)  # Track when comment was modified
    }
    
    await db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {"$set": update_data}
    )
    
    # Fetch and return updated comment
    updated_comment = await db.comments.find_one({"_id": ObjectId(comment_id)})
    return CommentResponse(**{
        "_id": str(updated_comment["_id"]),
        "blog_id": str(updated_comment["blog_id"]),
        "user_id": str(updated_comment["user_id"]),
        "user_name": updated_comment["user_name"],
        "text": updated_comment["text"],
        "created_at": updated_comment["created_at"],
        "updated_at": updated_comment.get("updated_at")
    })

@router.delete("/{comment_id}")
async def delete_comment(comment_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(comment_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid comment ID"
        )
    
    # First check if comment exists
    comment = await db.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found"
        )
    
    # Then check if user owns the comment
    if str(comment["user_id"]) != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": "Forbidden",
                "message": "You don't have permission to delete this comment"
            }
        )
        
    await db.blogs.update_one(
        {"_id": ObjectId(comment["blog_id"])},
        {"$inc": {"comment_count": -1}}
    )
    
    await db.comments.delete_one({"_id": ObjectId(comment_id)})
        
    return {"message": "Comment deleted successfully"}
