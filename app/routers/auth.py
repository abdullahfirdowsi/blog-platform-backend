from datetime import datetime
from bson import ObjectId
from fastapi import APIRouter, HTTPException, status, Depends, Response, Request
from fastapi.security import HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr

from app.models.models import (
    ForgotPassword, PasswordChange, ResetPassword, UserCreate,
    UserLogin, UserResponse, UserInDB, UsernameUpdate,
    EmailVerification, ResendEmailVerification
)
from app.core.auth import (
    get_password_hash, authenticate_user, create_access_token, create_refresh_token,
    get_current_user, verify_password, verify_token, get_user_by_email
)
from app.db.database import get_database
from app.core.config import settings
from app.services.email_service import email_service
from app.services.password_reset_service import (
    generate_reset_token, validate_reset_token, clear_reset_token
)
from app.services.email_verification_service import email_verification_service

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

class MessageResponse(BaseModel):
    message: str


# ==== ROUTES ====

@router.post("/register")
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
        "created_at": datetime.now(),
        "email_verified": False,
        "email_verification_token": None,
        "email_verification_token_expires": None
    }

    result = await db.users.insert_one(user_dict)
    
    # Generate and send email verification token
    try:
        verification_token = await email_verification_service.create_verification_token(normalized_email)
        if verification_token:
            await email_service.send_email_verification_email(normalized_email, verification_token)
    except Exception as e:
        # Log error but don't fail registration
        print(f"Failed to send verification email: {str(e)}")
    
    return {
        "message": "Registration successful! Please check your email to verify your account before logging in.",
        "user": {
            "id": str(result.inserted_id),
            "username": normalized_username,
            "email": normalized_email,
            "email_verified": False
        }
    }


@router.post("/login", response_model=LoginResponse)
async def login(user_credentials: UserLogin, response: Response):
    user = await authenticate_user(user_credentials.email, user_credentials.password)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if email verification is required
    if user == "email_not_verified":
        raise HTTPException(
            status_code=403,
            detail="Please verify your email address before logging in. Check your inbox for a verification link."
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

    if not current_user.password_hash or not verify_password(password_data.current_password, current_user.password_hash):
        raise HTTPException(status_code=400, detail="Current password is incorrect")

    new_password_hash = get_password_hash(password_data.new_password)
    await db.users.update_one(
        {"_id": ObjectId(current_user.id)},
        {"$set": {"password_hash": new_password_hash}}
    )

    return {"message": "Password changed successfully. Please login again."}


@router.post("/forgot-password")
async def forgot_password(forgot_password_data: ForgotPassword):
    """Request a password reset token via email."""
    db = await get_database()
    
    # Normalize email to lowercase
    normalized_email = forgot_password_data.email.lower().strip()
    
    # Check if user exists
    user = await db.users.find_one({"email": normalized_email})
    if not user:
        # Return error for unregistered email
        raise HTTPException(
            status_code=404,
            detail="No account found with this email address. Please check your email or register for a new account."
        )
    try:
        # Generate and save reset token
        reset_token = await generate_reset_token(user["_id"])
        
        # Send password reset email
        await email_service.send_password_reset_email(
            to_email=normalized_email,
            reset_token=reset_token
        )
        
        return {"message": "If an account with that email exists, a password reset link has been sent."}
    
    except Exception as e:
        # Log the error but don't expose it to the user
        print(f"Error in forgot password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your request. Please try again later."
        )


@router.post("/reset-password")
async def reset_password(reset_password_data: ResetPassword):
    """Reset password using a valid reset token."""
    db = await get_database()
    
    try:
        # Validate the reset token and get user ID
        user_id = await validate_reset_token(reset_password_data.token)
        
        if not user_id:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired reset token."
            )
        
        # Hash the new password
        new_password_hash = get_password_hash(reset_password_data.new_password)
        
        # Update user's password
        result = await db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password_hash": new_password_hash}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(
                status_code=404,
                detail="User not found."
            )
        
        # Clear the reset token
        await clear_reset_token(user_id)
        
        # Optionally send success confirmation email
        try:
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                await email_service.send_password_reset_success_email(user["email"])
        except Exception as e:
            # Log the error but don't fail the password reset
            print(f"Failed to send success email: {str(e)}")
        
        return {"message": "Password reset successfully. You can now login with your new password."}
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error but don't expose it to the user
        print(f"Error in reset password: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while resetting your password. Please try again later."
        )


@router.post("/verify-email")
async def verify_email(verification_data: EmailVerification):
    """Verify email address using verification token."""
    try:
        # Verify the email token
        email = await email_verification_service.verify_email_token(verification_data.token)
        
        if not email:
            raise HTTPException(
                status_code=400,
                detail="Invalid or expired verification token."
            )
        
        # Send success confirmation email
        try:
            await email_service.send_email_verification_success_email(email)
        except Exception as e:
            # Log the error but don't fail the verification
            print(f"Failed to send verification success email: {str(e)}")
        
        return {
            "message": "Email verified successfully! You can now log in to your account.",
            "email_verified": True
        }
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log the error but don't expose it to the user
        print(f"Error in email verification: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while verifying your email. Please try again later."
        )


@router.post("/resend-verification")
async def resend_verification_email(resend_data: ResendEmailVerification):
    """Resend email verification email."""
    db = await get_database()
    
    # Normalize email to lowercase
    normalized_email = resend_data.email.lower().strip()
    
    # Check if user exists
    user = await db.users.find_one({"email": normalized_email})
    if not user:
        raise HTTPException(
            status_code=404,
            detail="No account found with this email address."
        )
    
    # Check if email is already verified
    if user.get("email_verified", False):
        raise HTTPException(
            status_code=400,
            detail="Email is already verified. You can log in to your account."
        )
    
    try:
        # Generate and send new verification token
        verification_token = await email_verification_service.create_verification_token(normalized_email)
        
        if verification_token:
            await email_service.send_email_verification_email(normalized_email, verification_token)
        
        return {
            "message": "Verification email sent successfully. Please check your inbox."
        }
    
    except Exception as e:
        # Log the error but don't expose it to the user
        print(f"Error in resending verification email: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while sending the verification email. Please try again later."
        )
