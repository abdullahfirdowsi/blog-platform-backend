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
        json_encoders={ObjectId: str}
    )

# Blog Models
class BlogCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    tag_ids: Optional[List[PyObjectId]] = []
    main_image_url: Optional[str] = None
    published: bool = False

class BlogUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)
    tag_ids: Optional[List[PyObjectId]] = None
    main_image_url: Optional[str] = None
    published: Optional[bool] = None

class BlogResponse(BaseModel):
    id: PyObjectId = Field(alias="_id")
    user_id: PyObjectId
    title: str
    content: str
    tag_ids: List[PyObjectId] = []
    main_image_url: Optional[str] = None
    published: bool
    created_at: datetime
    updated_at: datetime
    
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
    tag_ids: List[PyObjectId] = []
    main_image_url: Optional[str] = None
    published: bool
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Comment Models
class CommentCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=500)

class CommentResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    blog_id: PyObjectId
    user_id: PyObjectId
    text: str
    created_at: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Like Models
class LikeCreate(BaseModel):
    isLiked: bool = True

class LikeResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    blog_id: PyObjectId
    user_id: PyObjectId
    isLiked: bool
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Tag Models
class TagCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)

class TagResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Image Models
class ImageCreate(BaseModel):
    image_url: List[str]

class ImageResponse(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    blog_id: PyObjectId
    image_url: List[str]
    uploaded_at: datetime
    
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

# Token Models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

