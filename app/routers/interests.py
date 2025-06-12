from fastapi import APIRouter, HTTPException, Depends
from typing import List
from datetime import datetime
from bson import ObjectId

from app.models.models import (
    UserInterestsCreate,
    UserInterestsUpdate,
    UserInterestsResponse,
    UserInDB
)
from app.core.auth import get_current_user
from app.db.database import get_database

router = APIRouter(prefix="/interests", tags=["interests"])


@router.post("/", response_model=UserInterestsResponse)
async def create_user_interests(
    interests: UserInterestsCreate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Create or update the user's interests."""
    db = await get_database()
    user_id = ObjectId(current_user.id)
    now = datetime.utcnow()

    existing = await db.user_interests.find_one({"user_id": user_id})

    if existing:
        await db.user_interests.update_one(
            {"user_id": user_id},
            {"$set": {"interests": interests.interests, "updated_at": now}}
        )
        data = await db.user_interests.find_one({"user_id": user_id})
    else:
        doc = {
            "user_id": user_id,
            "interests": interests.interests,
            "created_at": now,
            "updated_at": now
        }
        result = await db.user_interests.insert_one(doc)
        doc["_id"] = result.inserted_id
        data = doc

    # Format response
    data["_id"] = str(data["_id"])
    data["user_id"] = str(data["user_id"])
    return UserInterestsResponse(**data)


@router.get("/", response_model=UserInterestsResponse)
async def get_user_interests(current_user: UserInDB = Depends(get_current_user)):
    """Retrieve the current user's interests."""
    db = await get_database()
    user_id = ObjectId(current_user.id)

    interests = await db.user_interests.find_one({"user_id": user_id})
    if not interests:
        raise HTTPException(404, detail="User interests not found")

    interests["_id"] = str(interests["_id"])
    interests["user_id"] = str(interests["user_id"])
    return UserInterestsResponse(**interests)


@router.put("/", response_model=UserInterestsResponse)
async def update_user_interests(
    interests_update: UserInterestsUpdate,
    current_user: UserInDB = Depends(get_current_user)
):
    """Replace the user's entire interests array."""
    db = await get_database()
    user_id = ObjectId(current_user.id)
    now = datetime.utcnow()

    existing = await db.user_interests.find_one({"user_id": user_id})
    if not existing:
        raise HTTPException(404, detail="User interests not found. Create interests first.")

    await db.user_interests.update_one(
        {"user_id": user_id},
        {"$set": {"interests": interests_update.interests, "updated_at": now}}
    )

    updated = await db.user_interests.find_one({"user_id": user_id})
    updated["_id"] = str(updated["_id"])
    updated["user_id"] = str(updated["user_id"])
    return UserInterestsResponse(**updated)


@router.patch("/add")
async def add_interest(
    interest: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Add a single interest to the user's list (no duplicates)."""
    db = await get_database()
    user_id = ObjectId(current_user.id)
    now = datetime.utcnow()

    existing = await db.user_interests.find_one({"user_id": user_id})
    if not existing:
        raise HTTPException(404, detail="User interests not found. Create interests first.")

    await db.user_interests.update_one(
        {"user_id": user_id},
        {
            "$addToSet": {"interests": interest},
            "$set": {"updated_at": now}
        }
    )

    return {"message": f"Interest '{interest}' added successfully"}


@router.patch("/remove")
async def remove_interest(
    interest: str,
    current_user: UserInDB = Depends(get_current_user)
):
    """Remove a single interest from the user's list."""
    db = await get_database()
    user_id = ObjectId(current_user.id)
    now = datetime.utcnow()

    existing = await db.user_interests.find_one({"user_id": user_id})
    if not existing:
        raise HTTPException(404, detail="User interests not found.")

    await db.user_interests.update_one(
        {"user_id": user_id},
        {
            "$pull": {"interests": interest},
            "$set": {"updated_at": now}
        }
    )

    return {"message": f"Interest '{interest}' removed successfully"}


@router.delete("/")
async def delete_user_interests(current_user: UserInDB = Depends(get_current_user)):
    """Delete the current user's interests record."""
    db = await get_database()
    user_id = ObjectId(current_user.id)

    result = await db.user_interests.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(404, detail="User interests not found")

    return {"message": "User interests deleted successfully"}


@router.get("/suggestions", response_model=List[str])
async def get_interest_suggestions():
    """Return a list of common interest suggestions."""
    suggestions = [
        "Technology", "Programming", "Web Development", "Mobile Development", "Data Science",
        "Machine Learning", "Artificial Intelligence", "Cybersecurity", "Cloud Computing",
        "DevOps", "Blockchain", "Cryptocurrency", "Gaming", "Design", "UI/UX",
        "Business", "Entrepreneurship", "Marketing", "Finance", "Health", "Fitness",
        "Travel", "Food", "Photography", "Music", "Movies", "Books", "Sports",
        "Science", "Education", "Politics", "Environment", "Art", "Culture",
        "Fashion", "Lifestyle", "Personal Development", "Productivity", "Innovation"
    ]
    return suggestions
