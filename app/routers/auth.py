from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from app.models.models import (
    ForgotPassword, PasswordChange, ResetPassword, UserCreate,
    UserLogin, UserResponse, UserInDB, UsernameUpdate
)
from app.core.auth import (
    get_password_hash, authenticate_user, create_access_token, create_refresh_token,
    get_current_user, verify_password, verify_token, get_user_by_email
)
from app.db.database import get_database
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])


# ==== RESPONSE SCHEMAS ====

class UserInfo(BaseModel):
    id: str
    username: str
    email: EmailStr

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    message: str
    user: UserInfo

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    message: str


# ==== ROUTES ====

@router.post("/register", response_model=UserResponse)
async def register(user: UserCreate):
    db = await get_database()
    
    # Normalize email to lowercase
    normalized_email = user.email.lower().strip()
    normalized_username = user.username.lower().strip()

    if await db.users.find_one({"email": normalized_email}):
        raise HTTPException(status_code=400, detail="Email already registered")

    if await db.users.find_one({"username": normalized_username}):
        raise HTTPException(status_code=400, detail="Username already taken")

    hashed_password = get_password_hash(user.password)
    user_dict = {
        "username": normalized_username,
        "email": normalized_email,
        "password_hash": hashed_password,
        "refresh_token": None,
        "created_at": datetime.now()
    }

    result = await db.users.insert_one(user_dict)
    return UserResponse(
        _id=str(result.inserted_id),
        username=normalized_username,
        email=normalized_email,
        created_at=user_dict["created_at"]
    )


@router.post("/login", response_model=LoginResponse)
async def login(user_credentials: UserLogin, response: Response):
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})

    db = await get_database()
    await db.users.update_one({"_id": ObjectId(user.id)}, {"$set": {"refresh_token": refresh_token}})

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
        httponly=True,
        secure=True,  # ⚠️ Set to True in production
        samesite="none",
        path="/api/v1/auth"
    )

    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        message="Login successful",
        user=UserInfo(id=str(user.id), username=user.username, email=user.email)
    )


@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: Request, response: Response):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Authentication required. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    credentials_exception = HTTPException(
        status_code=401,
        detail="Invalid or expired refresh token. Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        token_data = verify_token(refresh_token, credentials_exception)
        user = await get_user_by_email(email=token_data.email)

        if user is None or user.refresh_token != refresh_token:
            raise credentials_exception

        access_token = create_access_token(data={"sub": user.email})
        new_refresh_token = create_refresh_token(data={"sub": user.email})

        db = await get_database()
        await db.users.update_one({"_id": ObjectId(user.id)}, {"$set": {"refresh_token": new_refresh_token}})

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 86400,
            httponly=True,
            secure=True,  # ⚠️ Set to True in production
            samesite="none",
            path="/api/v1/auth"
        )

        return RefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            message="Token refreshed successfully"
        )

    except Exception:
        response.delete_cookie(key="refresh_token", path="/api/v1/auth")
        raise credentials_exception


@router.post("/logout")
async def logout(request: Request, response: Response, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()
    await db.users.update_one({"_id": ObjectId(current_user.id)}, {"$set": {"refresh_token": None}})
    response.delete_cookie(key="refresh_token", path="/api/v1/auth", httponly=True, samesite="lax")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    return UserResponse(**current_user.dict())


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    db = await get_database()
    try:
        object_id = ObjectId(user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    user = await db.users.find_one({"_id": object_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_response = {
        "_id": str(user["_id"]),
        "username": user["username"],
        "email": user["email"],
        "created_at": user["created_at"],
        "full_name": user.get("full_name"),
        "profile_picture": user.get("profile_picture")
    }

    return UserResponse(**user_response)


@router.put("/update-username", response_model=UserResponse)
async def update_username(username_data: UsernameUpdate, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()

    existing_user = await db.users.find_one({
        "username": username_data.username,
        "_id": {"$ne": ObjectId(current_user.id)}
    })
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")

    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"username": username_data.username}}
    )

    updated_user = await db.users.find_one({"_id": ObjectId(current_user.id)})
    return UserResponse(
        _id=str(updated_user["_id"]),
        username=updated_user["username"],
        email=updated_user["email"],
        created_at=updated_user["created_at"]
    )


@router.post("/change-password")
async def change_password(password_data: PasswordChange, current_user: UserInDB = Depends(get_current_user)):
    db = await get_database()

    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    new_password_hash = get_password_hash(password_data.new_password)
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"password_hash": new_password_hash}}
    )

    return {"message": "Password changed successfully. Please login again."}
