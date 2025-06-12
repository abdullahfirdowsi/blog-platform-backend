from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.models import LikeResponse, MessageResponse, UserInDB
from app.core.auth import get_current_user
from app.db.database import get_database

router = APIRouter(prefix="/likes", tags=["likes"])


@router.post("/blogs/{blog_id}", response_model=LikeResponse | MessageResponse)
async def toggle_like(
    blog_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Like or Unlike a blog post.
    """
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    blog = await db.blogs.find_one({"_id": ObjectId(blog_id)})
    if not blog:
        raise HTTPException(status_code=404, detail="Blog not found")

    existing_like = await db.likes.find_one({
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id)
    })

    if existing_like:
        await db.likes.delete_one({"_id": existing_like["_id"]})
        await db.blogs.update_one(
            {"_id": ObjectId(blog_id)},
            {"$inc": {"likes_count": -1}}
        )
        return {"message": "Like removed successfully"}

    # Create new like
    like_dict = {
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id),
        "created_at": datetime.now()
    }

    result = await db.likes.insert_one(like_dict)
    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"likes_count": 1}}
    )

    like_dict["_id"] = str(result.inserted_id)
    like_dict["blog_id"] = str(like_dict["blog_id"])
    like_dict["user_id"] = str(like_dict["user_id"])

    return LikeResponse(**like_dict)


@router.get("/blogs/{blog_id}/count", response_model=int)
async def get_blog_likes_count(blog_id: str):
    """
    Get the total number of likes on a blog.
    """
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    return await db.likes.count_documents({"blog_id": ObjectId(blog_id)})


@router.get("/blogs/{blog_id}/my-like", response_model=LikeResponse)
async def get_my_like_for_blog(
    blog_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Check if the current user has liked a specific blog.
    """
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    like = await db.likes.find_one({
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id)
    })

    if not like:
        raise HTTPException(status_code=404, detail="You haven't liked this blog")

    like["_id"] = str(like["_id"])
    like["blog_id"] = str(like["blog_id"])
    like["user_id"] = str(like["user_id"])

    return LikeResponse(**like)


@router.delete("/blogs/{blog_id}")
async def remove_like(
    blog_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """
    Explicitly remove a like from a blog post.
    """
    db = await get_database()

    if not ObjectId.is_valid(blog_id):
        raise HTTPException(status_code=400, detail="Invalid blog ID")

    result = await db.likes.delete_one({
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id)
    })

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No like found for this blog")

    await db.blogs.update_one(
        {"_id": ObjectId(blog_id)},
        {"$inc": {"likes_count": -1}}
    )

    return {"message": "Like removed successfully"}


@router.get("/my-likes", response_model=List[LikeResponse])
async def get_my_likes(current_user: UserInDB = Depends(get_current_user)):
    """
    Get all blogs liked by the current user.
    """
    db = await get_database()

    cursor = db.likes.find({"user_id": ObjectId(current_user.id)})
    likes = await cursor.to_list(length=None)

    for like in likes:
        like["_id"] = str(like["_id"])
        like["blog_id"] = str(like["blog_id"])
        like["user_id"] = str(like["user_id"])

    return [LikeResponse(**like) for like in likes]
