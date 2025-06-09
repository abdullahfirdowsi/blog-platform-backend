from fastapi import APIRouter, HTTPException, status, Depends
from typing import List
from datetime import datetime
from models import UserInterestsCreate, UserInterestsUpdate, UserInterestsResponse, UserInDB
from auth import get_current_user
from database import get_database
from bson import ObjectId

router = APIRouter(prefix="/interests", tags=["interests"])

@router.post("/", response_model=UserInterestsResponse)
async def create_user_interests(interests: UserInterestsCreate, current_user: UserInDB = Depends(get_current_user)):
    """Create or update user interests"""
    db = await get_database()
    
    # Check if user already has interests
    existing_interests = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
    
    if existing_interests:
        # Update existing interests
        update_data = {
            "interests": interests.interests,
            "updated_at": datetime.utcnow()
        }
        
        await db.user_interests.update_one(
            {"user_id": ObjectId(current_user.id)},
            {"$set": update_data}
        )
        
        updated_interests = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
        # Convert ObjectIds to strings
        updated_interests["_id"] = str(updated_interests["_id"])
        updated_interests["user_id"] = str(updated_interests["user_id"])
        return UserInterestsResponse(**updated_interests)
    else:
        # Create new interests record
        interests_dict = {
            "user_id": ObjectId(current_user.id),
            "interests": interests.interests,  # This is the array of interests
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        
        result = await db.user_interests.insert_one(interests_dict)
        interests_dict["_id"] = str(result.inserted_id)
        interests_dict["user_id"] = str(interests_dict["user_id"])
        
        return UserInterestsResponse(**interests_dict)

@router.get("/", response_model=UserInterestsResponse)
async def get_user_interests(current_user: UserInDB = Depends(get_current_user)):
    """Get current user's interests"""
    db = await get_database()
    
    interests = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
    if not interests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User interests not found"
        )
    
    # Convert ObjectIds to strings
    interests["_id"] = str(interests["_id"])
    interests["user_id"] = str(interests["user_id"])
    
    return UserInterestsResponse(**interests)

@router.put("/", response_model=UserInterestsResponse)
async def update_user_interests(interests_update: UserInterestsUpdate, current_user: UserInDB = Depends(get_current_user)):
    """Update user interests (replaces entire interests array)"""
    db = await get_database()
    
    # Check if user has interests
    existing_interests = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
    if not existing_interests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User interests not found. Create interests first."
        )
    
    update_data = {
        "interests": interests_update.interests,  # Replace entire array
        "updated_at": datetime.utcnow()
    }
    
    await db.user_interests.update_one(
        {"user_id": ObjectId(current_user.id)},
        {"$set": update_data}
    )
    
    updated_interests = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
    # Convert ObjectIds to strings
    updated_interests["_id"] = str(updated_interests["_id"])
    updated_interests["user_id"] = str(updated_interests["user_id"])
    return UserInterestsResponse(**updated_interests)

@router.patch("/add")
async def add_interest(interest: str, current_user: UserInDB = Depends(get_current_user)):
    """Add a single interest to user's interests array"""
    db = await get_database()
    
    # Check if user has interests
    existing_interests = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
    if not existing_interests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User interests not found. Create interests first."
        )
    
    # Add interest if not already exists
    await db.user_interests.update_one(
        {"user_id": ObjectId(current_user.id)},
        {
            "$addToSet": {"interests": interest},  # $addToSet prevents duplicates
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": f"Interest '{interest}' added successfully"}

@router.patch("/remove")
async def remove_interest(interest: str, current_user: UserInDB = Depends(get_current_user)):
    """Remove a single interest from user's interests array"""
    db = await get_database()
    
    # Check if user has interests
    existing_interests = await db.user_interests.find_one({"user_id": ObjectId(current_user.id)})
    if not existing_interests:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User interests not found."
        )
    
    # Remove interest from array
    await db.user_interests.update_one(
        {"user_id": ObjectId(current_user.id)},
        {
            "$pull": {"interests": interest},  # $pull removes from array
            "$set": {"updated_at": datetime.utcnow()}
        }
    )
    
    return {"message": f"Interest '{interest}' removed successfully"}

@router.delete("/")
async def delete_user_interests(current_user: UserInDB = Depends(get_current_user)):
    """Delete entire user interests record"""
    db = await get_database()
    
    result = await db.user_interests.delete_one({"user_id": ObjectId(current_user.id)})
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User interests not found"
        )
    
    return {"message": "User interests deleted successfully"}

@router.get("/suggestions", response_model=List[str])
async def get_interest_suggestions():
    """Get common interest suggestions"""
    # Common interests suggestions
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

