from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator
from typing_extensions import Annotated
from bson import ObjectId

# Alias for ObjectId to avoid complex validation
PyObjectId = Annotated[str, Field(description="MongoDB ObjectId")]

# User Models

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if ' ' in v:
            raise ValueError('Username cannot contain spaces')
        return v

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    email: EmailStr
    created_at: datetime
    profile_picture: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    email: EmailStr
    password_hash: Optional[str] = None
    refresh_token: Optional[str] = None
    created_at: datetime
    email_verified: bool = False
    email_verification_token: Optional[str] = None
    email_verification_token_expires: Optional[datetime] = None
    profile_picture: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
        extra="ignore"
    )

# Blog Models

class BlogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tags: Optional[List[str]] = []
    main_image_url: Optional[str] = None
    published: bool = True

class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tags: Optional[List[str]] = None
    main_image_url: Optional[str] = None
    published: Optional[bool] = None

class BlogResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    username: Optional[str] = None
    profile_picture: Optional[str] = None
    title: str
    content: str
    tags: List[str] = []
    main_image_url: Optional[str] = None
    published: bool
    created_at: datetime
    updated_at: datetime
    comment_count: int = 0
    likes_count: int = 0

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class BlogInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    title: str
    content: str
    tags: List[str] = []
    main_image_url: Optional[str] = None
    published: bool
    created_at: datetime
    updated_at: datetime
    comment_count: Optional[int] = 0
    likes_count: Optional[int] = 0

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Image Models

class SingleImageResponse(BaseModel):
    success: bool
    imageUrl: Optional[str] = None
    message: Optional[str] = None

class S3ImageInfo(BaseModel):
    key: str
    url: str
    size: int
    lastModified: str

class S3ImagesListResponse(BaseModel):
    success: bool
    images: List[S3ImageInfo]

# Comment Models

class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

class CommentResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    blog_id: PyObjectId
    user_id: PyObjectId
    user_name: str
    text: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Like Models

class LikeCreate(BaseModel):
    pass

class LikeResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    blog_id: PyObjectId
    user_id: PyObjectId
    created_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Tag Models

class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    name: str

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Message Response

class MessageResponse(BaseModel):
    message: str

# User Interests Models

class UserInterestsCreate(BaseModel):
    interests: List[str] = Field(..., min_items=1, max_items=20)

class UserInterestsUpdate(BaseModel):
    interests: List[str] = Field(..., min_items=1, max_items=20)

class UserInterestsResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    interests: List[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# AI Summary Models

class BlogSummaryCreate(BaseModel):
    blog_id: str
    blog_title: str
    blog_content: str

class BlogSummaryInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    blog_id: str
    summary: str
    created_at: datetime

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str}
    }

class BlogSummaryResponse(BaseModel):
    blog_id: str
    summary: str
    created_at: datetime

# Blog Recommendation Models

class BlogRecommendationResponse(BaseModel):
    blog: BlogResponse
    relevance_score: float

class PaginatedBlogsResponse(BaseModel):
    blogs: List[BlogResponse]
    total: int
    page: int
    limit: int
    total_pages: int

# Token Models

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

# User Update Models

class UsernameUpdate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    
    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if ' ' in v:
            raise ValueError('Username cannot contain spaces')
        return v

class ProfilePictureUpdate(BaseModel):
    profile_picture: Optional[str] = None

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=6)

class ForgotPassword(BaseModel):
    email: EmailStr

class ResetPassword(BaseModel):
    token: str
    new_password: str = Field(..., min_length=6)

class EmailVerification(BaseModel):
    token: str

class ResendEmailVerification(BaseModel):
    email: EmailStr
