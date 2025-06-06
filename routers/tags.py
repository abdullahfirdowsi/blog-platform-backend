from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import List
from models import TagCreate, TagResponse, UserInDB
from auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/", response_model=TagResponse)
async def create_tag(tag: TagCreate, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    # Check if tag already exists (case-insensitive)
    existing_tag = await db.tags.find_one({"name": {"$regex": f"^{tag.name}$", "$options": "i"}})
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag already exists"
        )
    
    tag_dict = {
        "name": tag.name.lower()  # Store tags in lowercase for consistency
    }
    
    result = await db.tags.insert_one(tag_dict)
    tag_dict["id"] = str(result.inserted_id)
    
    return TagResponse(**tag_dict)

@router.get("/", response_model=List[TagResponse])
async def get_all_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    db = await get_database()
    
    cursor = db.tags.find({}).skip(skip).limit(limit).sort("name", 1)
    tags = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string and rename _id to id for each tag
    for tag in tags:
        tag["id"] = str(tag["_id"])
        del tag["_id"]
    
    return [TagResponse(**tag) for tag in tags]

@router.get("/search/{query}", response_model=List[TagResponse])
async def search_tags(
    query: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    db = await get_database()
    
    # Search tags by name (case-insensitive)
    search_filter = {"name": {"$regex": query, "$options": "i"}}
    
    cursor = db.tags.find(search_filter).skip(skip).limit(limit).sort("name", 1)
    tags = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string and rename _id to id for each tag
    for tag in tags:
        tag["id"] = str(tag["_id"])
        del tag["_id"]
    
    return [TagResponse(**tag) for tag in tags]

@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(tag_id: str):
    db = await get_database()
    
    if not ObjectId.is_valid(tag_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tag ID"
        )
    
    tag = await db.tags.find_one({"_id": ObjectId(tag_id)})
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Convert ObjectId to string and rename _id to id
    tag["id"] = str(tag["_id"])
    del tag["_id"]
    
    return TagResponse(**tag)

@router.delete("/{tag_id}")
async def delete_tag(tag_id: str, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    
    if not ObjectId.is_valid(tag_id):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tag ID"
        )
    
    # Check if tag exists
    tag = await db.tags.find_one({"_id": ObjectId(tag_id)})
    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
    
    # Remove tag from all blogs that use it
    await db.blogs.update_many(
        {"tag_ids": ObjectId(tag_id)},
        {"$pull": {"tag_ids": ObjectId(tag_id)}}
    )
    
    # Delete the tag
    await db.tags.delete_one({"_id": ObjectId(tag_id)})
    
    return {"message": "Tag deleted successfully"}

@router.get("/popular/", response_model=List[dict])
async def get_popular_tags(limit: int = Query(10, ge=1, le=50)):
    """Get most popular tags based on usage in blogs"""
    db = await get_database()
    
    # Aggregate pipeline to count tag usage
    pipeline = [
        {"$unwind": "$tag_ids"},
        {"$group": {"_id": "$tag_ids", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "tags",
                "localField": "_id",
                "foreignField": "_id",
                "as": "tag_info"
            }
        },
        {"$unwind": "$tag_info"},
        {
            "$project": {
                "_id": {"$toString": "$tag_info._id"},
                "name": "$tag_info.name",
                "usage_count": "$count"
            }
        }
    ]
    
    result = await db.blogs.aggregate(pipeline).to_list(length=limit)
    return result

