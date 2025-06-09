from fastapi import APIRouter, Body, HTTPException, status, Depends, Query
from typing import List, Optional
from models import MessageResponse, TagResponse, UserInDB
from auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/tags", tags=["tags"])

@router.post("/", response_model=MessageResponse)
async def create_tags(
    tag_names: List[str] = Body(default=[]),
    current_user: UserInDB = Depends(get_current_user)
):
    if not tag_names:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tag list cannot be empty"
        )

    db = await get_database()
    tag_names = [name.lower() for name in tag_names]

    # ✅ Only perform query if tag_names is not empty
    existing_tags = await db.tags.find({
        "$or": [{"name": {"$regex": f"^{name}$", "$options": "i"}} for name in tag_names]
    }).to_list(None)

    existing_names = {tag["name"].lower() for tag in existing_tags}
    
    tags_to_insert = [
        {"name": name}
        for name in tag_names
        if name.lower() not in existing_names
    ]

    if not tags_to_insert:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="All tags already exist"
        )

    await db.tags.insert_many(tags_to_insert)

    return {"message": "Tags created successfully"}


@router.get("/", response_model=List[TagResponse])
async def get_all_tags(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100)
):
    db = await get_database()
    
    cursor = db.tags.find({}).skip(skip).limit(limit).sort("name", 1)
    tags = await cursor.to_list(length=limit)
    
    # Convert ObjectId to string for each tag
    for tag in tags:
        tag["_id"] = str(tag["_id"])
    
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
    
    # Convert ObjectId to string for each tag
    for tag in tags:
        tag["_id"] = str(tag["_id"])
    
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
    
    # Convert ObjectId to string
    tag["_id"] = str(tag["_id"])
    
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
    db = await get_database()
    
    pipeline = [
        {"$unwind": "$tags"},  # Now unwinding the tags array (strings)
        {"$group": {"_id": "$tags", "count": {"$sum": 1}}},  # Group by tag name
        {"$sort": {"count": -1}},
        {"$limit": limit},
        {
            "$lookup": {
                "from": "tags",
                "localField": "_id",  # Now matching tag name to tag collection
                "foreignField": "name",
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