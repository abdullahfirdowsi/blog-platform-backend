from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from datetime import datetime
from models import UserCreate, UserLogin, UserResponse, UserInDB
from auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    get_current_user,
    verify_token,
    get_user_by_email,
    security
)
from database import get_database
from config import settings
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    db = await get_database()
    
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    existing_username = await db.users.find_one({"username": user.username})
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    user_dict = {
        "username": user.username,
        "email": user.email,
        "password_hash": hashed_password,
        "refresh_token": None,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_dict)
    
    # Create a new dictionary with only the fields needed by UserResponse
    response_dict = {
        "_id": str(result.inserted_id),
        "username": user.username,
        "email": user.email,
        "created_at": user_dict["created_at"]
    }
    
    return UserResponse(**response_dict)

@router.post("/login")
async def login(user_credentials: UserLogin, response: Response):
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Store refresh token in database
    db = await get_database()
    await db.users.update_one(
        {"_id": user.id},
        {"$set": {"refresh_token": refresh_token}}
    )
    
    # Set refresh token as HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # Convert days to seconds
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Login successful"
    }

@router.post("/refresh")
async def refresh_token(request: Request, response: Response):
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify refresh token
    token_data = verify_token(refresh_token, credentials_exception)
    user = await get_user_by_email(email=token_data.email)
    
    if user is None or user.refresh_token != refresh_token:
        raise credentials_exception
    
    # Create new tokens
    access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    # Update refresh token in database
    db = await get_database()
    await db.users.update_one(
        {"_id": user.id},
        {"$set": {"refresh_token": new_refresh_token}}
    )
    
    # Update refresh token cookie
    response.set_cookie(
        key="refresh_token",
        value=new_refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax"
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": "Token refreshed successfully"
    }

@router.post("/logout")
async def logout(request: Request, response: Response, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    await db.users.update_one(
        {"_id": current_user.id},
        {"$set": {"refresh_token": None}}
    )
    
    # Clear refresh token cookie
    response.delete_cookie(key="refresh_token")
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return UserResponse(**current_user.dict())

