from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List
from datetime import datetime, timezone
from bson import ObjectId

from app.models.models import CommentCreate, CommentResponse, UserInDB
from app.core.auth import get_current_user
from app.db.database import get_database

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("/blogs/{blog_id}", response_model=CommentResponse)
async def create_comment(
    blog_id: str,
    comment: CommentCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Create a comment for a given blog.
    """
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    comment_dict = {
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id),
        "user_name": current_user.username,
        "text": comment.text,
        "created_at": datetime.now(),
        "updated_at": None
    }

    result = await db.comments.insert_one(comment_dict)

    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"comment_count": 1}}
    )

    comment_dict["_id"] = str(result.inserted_id)
    comment_dict["blog_id"] = str(comment_dict["blog_id"])
    comment_dict["user_id"] = str(comment_dict["user_id"])

    return CommentResponse(**comment_dict)


@router.get("/blogs/{blog_id}", response_model=List[CommentResponse])
async def get_blog_comments(
    blog_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get comments for a specific blog.
    """
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    cursor = db.comments.find(
        {"blog_id": ObjectId(blog_id)}
    ).skip(skip).limit(limit).sort("created_at", -1)

    comments = await cursor.to_list(length=limit)

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
    """
    Retrieve comments made by the current user.
    """
    db = await get_database()

    cursor = db.comments.find(
        {"user_id": ObjectId(current_user.id)}
    ).skip(skip).limit(limit).sort("created_at", -1)

    comments = await cursor.to_list(length=limit)

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
    """
    Update a comment made by the current user.
    """
    db = await get_database()

    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=400, detail="Invalid comment ID")

    existing_comment = await db.comments.find_one({
        "_id": ObjectId(comment_id),
        "user_id": ObjectId(current_user.id)
    })

    if not existing_comment:
        raise HTTPException(
            status_code=404,
            detail="Comment not found or permission denied"
        )

    await db.comments.update_one(
        {"_id": ObjectId(comment_id)},
        {
            "$set": {
                "text": comment_update.text,
                "updated_at": datetime.now(timezone.utc)
            }
        }
    )

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
async def delete_comment(
    comment_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Delete a comment made by the current user.
    """
    db = await get_database()

    if not ObjectId.is_valid(comment_id):
        raise HTTPException(status_code=400, detail="Invalid comment ID")

    comment = await db.comments.find_one({"_id": ObjectId(comment_id)})
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")

    if str(comment["user_id"]) != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You don't have permission to delete this comment"
        )

    await db.blogs.update_one(
        {"_id": ObjectId(comment["blog_id"])},
        {"$inc": {"comment_count": -1}}
    )

    await db.comments.delete_one({"_id": ObjectId(comment_id)})

    return {"message": "Comment deleted successfully"}
