from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from fastapi.responses import RedirectResponse
from datetime import datetime
from models import UserCreate, UserLogin, UserResponse, UserInDB, ChangePasswordRequest, ProfileUpdateRequest
from pydantic import BaseModel
import httpx
from google.auth.transport import requests
from google.oauth2 import id_token
import secrets
import urllib.parse

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse
    message: str

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse
    message: str
    
from auth import (
    get_password_hash, 
    authenticate_user, 
    create_access_token, 
    create_refresh_token,
    get_current_user,
    verify_token,
    get_user_by_email,
    verify_password,
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
        "full_name": user.full_name,
        "bio": None,
        "profile_picture": None,
        "google_id": None,
        "is_active": True,
        "role": "user",
        "refresh_token": None,
        "created_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_dict)
    
    # Create a new dictionary with only the fields needed by UserResponse
    response_dict = {
        "_id": str(result.inserted_id),
        "username": user.username,
        "email": user.email,
        "full_name": user.full_name,
        "bio": None,
        "profile_picture": None,
        "google_id": None,
        "is_active": True,
        "role": "user",
        "created_at": user_dict["created_at"],
        "has_password": True  # Regular users have passwords
    }
    
    return UserResponse(**response_dict)

@router.post("/login", response_model=LoginResponse)
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
        {"_id": ObjectId(user.id)},
        {"$set": {"refresh_token": refresh_token}}
    )
    
    # Set refresh token as secure HTTP-only cookie
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        path="/api/v1/auth"  # Restrict cookie to auth endpoints only
    )
    
    # Prepare user response
    user_data = user.dict()
    user_data["has_password"] = bool(user.password_hash)
    # Ensure all required fields are present
    user_data.setdefault("full_name", None)
    user_data.setdefault("bio", None)
    user_data.setdefault("is_active", True)
    user_data.setdefault("role", "user")
    user_response = UserResponse(**user_data)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user=user_response,
        message="Login successful"
    )

@router.post("/refresh", response_model=RefreshResponse)
async def refresh_token(request: Request, response: Response):
    """Refresh access token using secure HTTP-only cookie"""
    # Get refresh token from cookie
    refresh_token = request.cookies.get("refresh_token")
    
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please login again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired refresh token. Please login again.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
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
            {"_id": ObjectId(user.id)},
            {"$set": {"refresh_token": new_refresh_token}}
        )
        
        # Update refresh token cookie (rotate refresh token for security)
        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/api/v1/auth"
        )
        
        # Prepare user response
        user_data = user.dict()
        user_data["has_password"] = bool(user.password_hash)
        # Ensure all required fields are present
        user_data.setdefault("full_name", None)
        user_data.setdefault("bio", None)
        user_data.setdefault("is_active", True)
        user_data.setdefault("role", "user")
        user_response = UserResponse(**user_data)
        
        return RefreshResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response,
            message="Token refreshed successfully"
        )
    
    except Exception as e:
        # Clear invalid refresh token cookie
        response.delete_cookie(key="refresh_token", path="/api/v1/auth")
        raise credentials_exception


@router.post("/logout")
async def logout(request: Request, response: Response, current_user: UserInDB = Depends(get_current_user)):
    """Logout user and invalidate all tokens"""
    db = await get_database()
    
    # Invalidate refresh token in database
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"refresh_token": None}}
    )
    
    # Clear refresh token cookie
    response.delete_cookie(
        key="refresh_token", 
        path="/api/v1/auth",
        httponly=True,
        samesite="lax"
    )
    
    return {"message": "Successfully logged out"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: UserInDB = Depends(get_current_user)):
    # Create user response with all profile fields
    user_data = current_user.dict()
    user_data["has_password"] = bool(current_user.password_hash)
    # Ensure all required fields are present
    user_data.setdefault("full_name", None)
    user_data.setdefault("bio", None)
    user_data.setdefault("is_active", True)
    user_data.setdefault("role", "user")
    return UserResponse(**user_data)

@router.post("/change-password")
async def change_password(
    password_data: ChangePasswordRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Change user password"""
    # Check if passwords match
    if password_data.new_password != password_data.confirm_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password and confirmation password do not match"
        )
    
    # Check if user has a password (OAuth users might not have one)
    if not current_user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot change password for OAuth accounts"
        )
    
    # Verify current password
    if not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    # Hash new password
    new_password_hash = get_password_hash(password_data.new_password)
    
    # Update password in database
    db = await get_database()
    result = await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"password_hash": new_password_hash}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update password"
        )
    
    return {"message": "Password changed successfully"}

@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: ProfileUpdateRequest,
    current_user: UserInDB = Depends(get_current_user)
):
    """Update user profile information"""
    db = await get_database()
    update_fields = {}
    
    # Check what fields need to be updated
    if profile_data.username is not None:
        # Check if username is already taken by another user
        existing_user = await db.users.find_one({
            "username": profile_data.username,
            "_id": {"$ne": ObjectId(current_user.id)}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        update_fields["username"] = profile_data.username
    
    if profile_data.email is not None:
        # Check if email is already taken by another user
        existing_user = await db.users.find_one({
            "email": profile_data.email,
            "_id": {"$ne": ObjectId(current_user.id)}
        })
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        update_fields["email"] = profile_data.email
    
    if profile_data.full_name is not None:
        update_fields["full_name"] = profile_data.full_name
    
    if profile_data.bio is not None:
        update_fields["bio"] = profile_data.bio
    
    if profile_data.profile_picture is not None:
        update_fields["profile_picture"] = profile_data.profile_picture
    
    # If no fields to update, return current user
    if not update_fields:
        user_data = current_user.dict()
        user_data["has_password"] = bool(current_user.password_hash)
        # Ensure all required fields are present
        user_data.setdefault("full_name", None)
        user_data.setdefault("bio", None)
        user_data.setdefault("is_active", True)
        user_data.setdefault("role", "user")
        return UserResponse(**user_data)
    
    # Update user in database
    result = await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": update_fields}
    )
    
    if result.modified_count == 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )
    
    # Fetch updated user data
    updated_user = await get_user_by_email(current_user.email if profile_data.email is None else profile_data.email)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch updated user data"
        )
    
    # Return updated user response
    user_data = updated_user.dict()
    user_data["has_password"] = bool(updated_user.password_hash)
    # Ensure all required fields are present
    user_data.setdefault("full_name", None)
    user_data.setdefault("bio", None)
    user_data.setdefault("is_active", True)
    user_data.setdefault("role", "user")
    return UserResponse(**user_data)

# Google OAuth2 Models
class GoogleAuthRequest(BaseModel):
    token: str

class GoogleLoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserResponse
    message: str
    is_new_user: bool

# Google OAuth2 endpoints
@router.get("/google")
async def google_auth():
    """Initiate Google OAuth flow"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    # Generate a random state for CSRF protection
    state = secrets.token_urlsafe(32)
    
    # Build Google OAuth URL
    google_auth_url = (
        "https://accounts.google.com/o/oauth2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={urllib.parse.quote(settings.GOOGLE_REDIRECT_URI)}&"
        "scope=openid email profile&"
        "response_type=code&"
        "access_type=offline&"
        f"state={state}"
    )
    
    return {"auth_url": google_auth_url, "state": state}

@router.post("/google", response_model=GoogleLoginResponse)
async def google_login(google_request: GoogleAuthRequest, response: Response):
    """Authenticate user with Google ID token"""
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    try:
        # Verify the Google ID token
        id_info = id_token.verify_oauth2_token(
            google_request.token, 
            requests.Request(), 
            settings.GOOGLE_CLIENT_ID
        )
        
        # Extract user information from Google token
        google_user_id = id_info['sub']
        email = id_info['email']
        name = id_info.get('name', '')
        picture = id_info.get('picture', '')
        
        db = await get_database()
        
        # Check if user exists
        user_doc = await db.users.find_one({"email": email})
        is_new_user = False
        
        if not user_doc:
            # Create new user from Google account
            is_new_user = True
            
            # Generate username from email or name
            username = email.split('@')[0]
            
            # Ensure username is unique
            counter = 1
            original_username = username
            while await db.users.find_one({"username": username}):
                username = f"{original_username}{counter}"
                counter += 1
            
            user_dict = {
                "username": username,
                "email": email,
                "password_hash": None,  # No password for OAuth users
                "full_name": name if name else None,
                "bio": None,
                "google_id": google_user_id,
                "profile_picture": picture,
                "is_active": True,
                "role": "user",
                "refresh_token": None,
                "created_at": datetime.utcnow()
            }
            
            result = await db.users.insert_one(user_dict)
            user_dict["_id"] = result.inserted_id
            user_doc = user_dict
        else:
            # Update existing user's Google info if needed
            await db.users.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {
                    "google_id": google_user_id,
                    "profile_picture": picture,
                    "full_name": name if name else user_doc.get("full_name")
                }}
            )
        
        # Create tokens
        access_token = create_access_token(data={"sub": email})
        refresh_token = create_refresh_token(data={"sub": email})
        
        # Store refresh token in database
        await db.users.update_one(
            {"_id": user_doc["_id"]},
            {"$set": {"refresh_token": refresh_token}}
        )
        
        # Set refresh token as secure HTTP-only cookie
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
            httponly=True,
            secure=False,  # Set to True in production with HTTPS
            samesite="lax",
            path="/api/v1/auth"
        )
        
        # Prepare user response
        user_response = UserResponse(
            _id=str(user_doc["_id"]),
            username=user_doc["username"],
            email=user_doc["email"],
            full_name=user_doc.get("full_name"),
            bio=user_doc.get("bio"),
            profile_picture=user_doc.get("profile_picture"),
            google_id=user_doc.get("google_id"),
            is_active=user_doc.get("is_active", True),
            role=user_doc.get("role", "user"),
            created_at=user_doc["created_at"],
            has_password=bool(user_doc.get("password_hash"))
        )
        
        return GoogleLoginResponse(
            access_token=access_token,
            token_type="bearer",
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            user=user_response,
            message="Google login successful",
            is_new_user=is_new_user
        )
        
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )

@router.get("/callback")
async def google_callback(code: str, state: str, response: Response):
    """Handle Google OAuth callback (for web flow)"""
    if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail="Google OAuth not configured"
        )
    
    try:
        # Exchange authorization code for tokens
        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.GOOGLE_REDIRECT_URI,
                }
            )
            
            if token_response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange code for token"
                )
            
            token_data = token_response.json()
            id_token_str = token_data.get("id_token")
            
            if not id_token_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No ID token received"
                )
            
            # Process the login using the ID token
            google_request = GoogleAuthRequest(token=id_token_str)
            login_result = await google_login(google_request, response)
            
            # Redirect to frontend with success
            frontend_url = "http://localhost:4200/auth/callback"
            redirect_url = f"{frontend_url}?success=true&token={login_result.access_token}"
            
            return RedirectResponse(url=redirect_url)
            
    except HTTPException:
        raise
    except Exception as e:
        # Redirect to frontend with error
        frontend_url = "http://localhost:4200/auth/callback"
        redirect_url = f"{frontend_url}?error=google_auth_failed&message={urllib.parse.quote(str(e))}"
        return RedirectResponse(url=redirect_url)

