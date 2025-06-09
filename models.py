from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import Optional, List, Annotated
from datetime import datetime
from bson import ObjectId

# Simple type alias for ObjectId to avoid complex Pydantic validation
PyObjectId = Annotated[str, Field(description="MongoDB ObjectId")]

# User Models
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=20)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    email: EmailStr
    created_at: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

class UserInDB(BaseModel):
    id: PyObjectId = Field(alias="_id")
    username: str
    email: EmailStr
    password_hash: str
    refresh_token: Optional[str] = None
    created_at: datetime
    
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
    title: str
    content: str
    tags: List[str] = []
    main_image_url: Optional[str] = None
    published: bool
    created_at: datetime
    updated_at: datetime
    comment_count: int = Field(default=0)
    likes_count: int = Field(default=0)
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str},
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
    
#image models
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

# Blog Recommendation Models
class BlogRecommendationResponse(BaseModel):
    blog: BlogResponse
    relevance_score: float

class PaginatedBlogsResponse(BaseModel):
    blogs: List[BlogRecommendationResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

# Token Models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

