from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from datetime import datetime
from models import ImageCreate, ImageResponse, UserInDB
from auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/images", tags=["images"])

@router.post("/blogs/{blog_id}", response_model=ImageResponse)
async def add_images_to_blog(
    blog_id: str,
    image_data: ImageCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    # Check if blog exists and belongs to current user
    blog = await db.blogs.find_one({"_id": ObjectId(blog_id), "user_id": current_user.id})
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found or you don't have permission to add images"
        )
    
    # Check if images already exist for this blog
    existing_images = await db.images.find_one({"blog_id": ObjectId(blog_id)})
    
    if existing_images:
        # Update existing images
        await db.images.update_one(
            {"blog_id": ObjectId(blog_id)},
            {
                "$set": {
                    "image_url": image_data.image_url,
                    "uploaded_at": datetime.utcnow()
                }
            }
        )
        updated_images = await db.images.find_one({"blog_id": ObjectId(blog_id)})
        return ImageResponse(**updated_images)
    else:
        # Create new image record
        image_dict = {
            "blog_id": ObjectId(blog_id),
            "image_url": image_data.image_url,
            "uploaded_at": datetime.utcnow()
        }
        
        result = await db.images.insert_one(image_dict)
        image_dict["_id"] = result.inserted_id
        
        return ImageResponse(**image_dict)

@router.get("/blogs/{blog_id}", response_model=ImageResponse)
async def get_blog_images(blog_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    images = await db.images.find_one({"blog_id": ObjectId(blog_id)})
    if not images:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No images found for this blog"
        )
    
    return ImageResponse(**images)

@router.put("/blogs/{blog_id}", response_model=ImageResponse)
async def update_blog_images(
    blog_id: str,
    image_data: ImageCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    # Check if blog exists and belongs to current user
    blog = await db.blogs.find_one({"_id": ObjectId(blog_id), "user_id": current_user.id})
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found or you don't have permission to update images"
        )
    
    # Check if images exist for this blog
    existing_images = await db.images.find_one({"blog_id": ObjectId(blog_id)})
    if not existing_images:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No images found for this blog"
        )
    
    # Update images
    await db.images.update_one(
        {"blog_id": ObjectId(blog_id)},
        {
            "$set": {
                "image_url": image_data.image_url,
                "uploaded_at": datetime.utcnow()
            }
        }
    )
    
    updated_images = await db.images.find_one({"blog_id": ObjectId(blog_id)})
    return ImageResponse(**updated_images)

@router.delete("/blogs/{blog_id}")
async def delete_blog_images(
    blog_id: str,
    current_user: UserInDB = Depends(get_current_user)
):
    db = await get_database()
    
    if not ObjectId.is_valid(blog_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid blog ID"
        )
    
    # Check if blog exists and belongs to current user
    blog = await db.blogs.find_one({"_id": ObjectId(blog_id), "user_id": current_user.id})
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found or you don't have permission to delete images"
        )
    
    result = await db.images.delete_one({"blog_id": ObjectId(blog_id)})
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No images found for this blog"
        )
    
    return {"message": "Images deleted successfully"}

@router.get("/my-images", response_model=List[ImageResponse])
async def get_my_images(
    current_user: UserInDB = Depends(get_current_user),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """Get all images from user's blogs"""
    db = await get_database()
    
    # First get all blog IDs belonging to the current user
    user_blogs = await db.blogs.find({"user_id": current_user.id}, {"_id": 1}).to_list(length=None)
    blog_ids = [blog["_id"] for blog in user_blogs]
    
    if not blog_ids:
        return []
    
    # Get images for user's blogs
    cursor = db.images.find({"blog_id": {"$in": blog_ids}}).skip(skip).limit(limit).sort("uploaded_at", -1)
    images = await cursor.to_list(length=limit)
    
    return [ImageResponse(**image) for image in images]

