from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from models import LikeCreate, LikeResponse, UserInDB
from auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/likes", tags=["likes"])

@router.post("/blogs/{blog_id}", response_model=LikeResponse)
async def toggle_like(
    blog_id: str,
    like_data: LikeCreate,
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
    
    # Check if user already liked/disliked this blog
    existing_like = await db.likes.find_one({
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if existing_like:
        # Update existing like
        await db.likes.update_one(
            {"_id": existing_like["_id"]},
            {"$set": {"isLiked": like_data.isLiked}}
        )
        existing_like["isLiked"] = like_data.isLiked
        # Convert ObjectIds to strings
        existing_like["_id"] = str(existing_like["_id"])
        existing_like["blog_id"] = str(existing_like["blog_id"])
        existing_like["user_id"] = str(existing_like["user_id"])
        return LikeResponse(**existing_like)
    else:
        # Create new like
        like_dict = {
            "blog_id": ObjectId(blog_id),
            "user_id": ObjectId(current_user.id),
            "isLiked": like_data.isLiked
        }
        
        result = await db.likes.insert_one(like_dict)
        like_dict["_id"] = str(result.inserted_id)
        like_dict["blog_id"] = str(like_dict["blog_id"])
        like_dict["user_id"] = str(like_dict["user_id"])
        
        return LikeResponse(**like_dict)

@router.get("/blogs/{blog_id}/count")
async def get_blog_likes_count(blog_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    likes_count = await db.likes.count_documents({
        "blog_id": ObjectId(blog_id),
        "isLiked": True
    })
    
    dislikes_count = await db.likes.count_documents({
        "blog_id": ObjectId(blog_id),
        "isLiked": False
    })
    
    return {
        "blog_id": blog_id,
        "likes_count": likes_count,
        "dislikes_count": dislikes_count
    }

@router.get("/blogs/{blog_id}/my-like", response_model=LikeResponse)
async def get_my_like_for_blog(
    blog_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    like = await db.likes.find_one({
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if not like:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
        detail="No like/dislike found for this blog"
    )
    
    # Convert ObjectIds to strings
    like["_id"] = str(like["_id"])
    like["blog_id"] = str(like["blog_id"])
    like["user_id"] = str(like["user_id"])
    
    return LikeResponse(**like)

@router.delete("/blogs/{blog_id}")
async def remove_like(
    blog_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    result = await db.likes.delete_one({
        "blog_id": ObjectId(blog_id),
        "user_id": ObjectId(current_user.id)
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No like/dislike found for this blog"
        )
    
    return {"message": "Like/dislike removed successfully"}

@router.get("/my-likes", response_model=List[LikeResponse])
async def get_my_likes(current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    cursor = db.likes.find({"user_id": ObjectId(current_user.id)})
    likes = await cursor.to_list(length=None)
    
    # Convert ObjectIds to strings for each like
    for like in likes:
        like["_id"] = str(like["_id"])
        like["blog_id"] = str(like["blog_id"])
        like["user_id"] = str(like["user_id"])
    
    return [LikeResponse(**like) for like in likes]

