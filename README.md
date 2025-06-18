# BlogPlatform Backend API 🚀

> High-performance Python backend with AI-powered features, ML recommendations, enterprise-grade security, and comprehensive email services.

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-4EA94B?style=for-the-badge&logo=mongodb&logoColor=white)](https://www.mongodb.com/)
[![JWT](https://img.shields.io/badge/JWT-000000?style=for-the-badge&logo=JSON%20web%20tokens&logoColor=white)](https://jwt.io/)
[![AWS](https://img.shields.io/badge/AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)](https://aws.amazon.com/)
[![Google AI](https://img.shields.io/badge/Google_AI-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

## 📋 Table of Contents

- [Overview](#overview)
- [🌟 Key Features](#-key-features)
- [🏗️ Architecture](#️-architecture)
- [🚀 Quick Start](#-quick-start)
- [🔧 Configuration](#-configuration)
- [📊 API Documentation](#-api-documentation)
- [🤖 AI Integration](#-ai-integration)
- [🔒 Security](#-security)
- [🧪 Testing](#-testing)
- [🚀 Deployment](#-deployment)
- [🤝 Contributing](#-contributing)

## Overview

BlogPlatform Backend is a modern, high-performance REST API built with FastAPI, featuring AI-powered content recommendations, real-time collaboration, and enterprise-grade security. It serves as the backbone for a sophisticated blogging platform with advanced features like ML-based content discovery and automated AI summarization.

### 🎯 Why This Backend?

- **🔥 Performance**: Async/await architecture with 10x faster response times
- **🧠 AI-Powered**: Google Gemini integration for intelligent blog summarization
- **🔒 Enterprise Security**: JWT + refresh token rotation, bcrypt hashing, email verification
- **📧 Email Services**: Professional email templates, SMTP integration, verification & password reset
- **📈 Scalable**: Microservice-ready architecture with horizontal scaling
- **🤖 ML Recommendations**: Advanced TF-IDF vectorization with cosine similarity engine
- **☁️ Cloud Native**: AWS S3 integration, MongoDB Atlas ready
- **👤 User Management**: Profile pictures, comprehensive user preferences

## 🌟 Key Features

### ⚡ Core API Features
- **RESTful Design**: Clean, intuitive API endpoints with OpenAPI documentation
- **Async Operations**: Non-blocking I/O for maximum throughput
- **Auto-Generated Docs**: Interactive Swagger UI and ReDoc documentation
- **Input Validation**: Comprehensive request/response validation with Pydantic
- **Error Handling**: Structured error responses with proper HTTP status codes

### 🔐 Authentication & Security
- **JWT Authentication**: Short-lived access tokens (30 min) + long-lived refresh tokens (7 days)
- **Email Verification**: Mandatory email verification before account activation
- **Password Reset**: Secure token-based password recovery with email confirmation
- **HTTP-Only Cookies**: Secure refresh token storage
- **Password Security**: Bcrypt hashing with salt
- **CORS Protection**: Configurable cross-origin resource sharing
- **Input Sanitization**: Comprehensive validation with Pydantic models
- **Token Security**: Automatic token rotation and invalidation

### 🤖 AI & Machine Learning
- **Intelligent Blog Summarization**: Google Gemini AI generates concise 2-3 sentence summaries
- **Advanced Content Recommendations**: ML-powered discovery using TF-IDF vectorization
- **Smart Similarity Engine**: Cosine similarity with n-gram analysis and content weighting
- **User Interest Profiling**: Personalized content based on user preferences and behavior
- **Engagement Analytics**: Multi-factor scoring (recency, engagement, content relevance)
- **Text Processing**: Advanced preprocessing with stop-word removal and keyword extraction

### 📊 Data Management
- **MongoDB Integration**: Async operations with Motor driver
- **Schema Validation**: Pydantic models for data integrity
- **Efficient Queries**: Optimized database operations with indexing
- **Pagination**: Memory-efficient data loading

### ☁️ Cloud Integration
- **AWS S3**: Scalable image storage with metadata management
- **Google AI**: Gemini 1.5 Flash for intelligent content analysis
- **Email Services**: SMTP integration with Gmail and custom providers
- **Environment Management**: Flexible configuration for development/production

### 📧 Email System
- **Professional Templates**: Modern HTML email templates with responsive design
- **Email Verification**: Automated account verification with secure tokens
- **Password Recovery**: Secure password reset with token expiration
- **Success Notifications**: Confirmation emails for security actions
- **SMTP Integration**: Support for Gmail, custom SMTP servers

## 🏗️ Architecture

### System Design

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │    MongoDB      │    │    AWS S3       │
│   Application   │◄──►│    Database     │    │  Image Storage  │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Google Gemini  │    │   ML Pipeline   │    │   JWT Service   │
│   AI Service    │    │  Recommendations│    │  Authentication │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Email Service  │    │   TF-IDF Engine │    │ Token Security  │
│  SMTP/Templates │    │ Cosine Similarity│    │ Verification   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Project Structure

```
backend/
├── app/
│   ├── core/                    # Core functionality
│   │   ├── __init__.py
│   │   ├── auth.py             # JWT authentication logic
│   │   └── config.py           # Configuration management
│   ├── db/                     # Database layer
│   │   ├── __init__.py
│   │   └── database.py         # MongoDB connection & setup
│   ├── models/                 # Data models
│   │   ├── __init__.py
│   │   └── models.py           # Pydantic schemas
│   ├── routers/                # API endpoints
│   │   ├── __init__.py
│   │   ├── auth.py             # Authentication routes
│   │   ├── blogs.py            # Blog CRUD operations
│   │   ├── comments.py         # Comment system
│   │   ├── likes.py            # Like/dislike functionality
│   │   ├── tags.py             # Tag management
│   │   ├── images.py           # Image handling (S3)
│   │   ├── interests.py        # User interests
│   │   └── summaries.py        # AI summarization
│   ├── services/               # Business logic
│       ├── __init__.py
│       ├── ai_summary.py       # Google Gemini AI summarization
│       ├── email_service.py    # SMTP email services
│       ├── email_verification_service.py  # Email verification logic
│       ├── password_reset_service.py      # Password reset handling
│       └── recommendation_service.py      # ML recommendation engine
│   └── templates/              # Email templates
│       └── email_templates.py  # Professional HTML email templates
├── main.py                     # Application entry point
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── run.bat                    # Windows run script
└── README.md                  # This file
```

### Database Schema

#### Collections Overview

| Collection | Purpose | Key Features |
|------------|---------|-------------|
| `users` | User accounts | JWT refresh tokens, bcrypt passwords, email verification |
| `blogs` | Blog posts | Block-based content, tags, engagement metrics, AI summaries |
| `comments` | Comment threads | User references, timestamps, threaded discussions |
| `likes` | Engagement tracking | User-blog relationships, like counts |
| `tags` | Content categorization | Auto-creation, search indexing, ML features |
| `images` | Media management | S3 metadata, blog associations, profile pictures |
| `user_interests` | ML personalization | Interest tracking, recommendation algorithms |

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+** with pip
- **MongoDB** (local or Atlas)
- **Git**

### 1. Clone & Setup

```bash
# Clone the repository
git clone <repository-url>
cd BlogPlatform/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

### 2. Install Dependencies

```bash
# Install all dependencies
# Key Dependencies:
# - fastapi==0.115.12          # High-performance web framework
# - uvicorn==0.34.3            # ASGI server
# - motor==3.7.1               # Async MongoDB driver
# - python-jose==3.5.0         # JWT token handling
# - passlib==1.7.4             # Password hashing
# - google-generativeai==0.8.5 # Google Gemini AI
# - scikit-learn==1.6.1        # ML for recommendations
# - boto3==1.38.32             # AWS S3 integration
# - pydantic==2.11.5           # Data validation
# - python-multipart==0.0.20   # File upload support

pip install -r requirements.txt

# Verify installation
pip list | grep fastapi
```

### 3. Environment Configuration

```bash
# Create .env file with required configurations
# See configuration section below for all required variables

# Edit .env with your configurations
notepad .env  # Windows
# nano .env  # macOS/Linux
```

### 4. Run the Application

```bash
# Development mode with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Windows batch script
run.bat
```

### 5. Verify Installation

- **API Health Check**: http://localhost:8000/health
- **Interactive Docs**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Root Endpoint**: http://localhost:8000/

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following configuration:

```env
# Database Configuration
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/blogging?retryWrites=true&w=majority

# Authentication Settings
SECRET_KEY=your-super-secret-256-bit-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=15

# AWS S3 Configuration
AWS_ACCESS_KEY_ID=your-aws-access-key-id
AWS_SECRET_ACCESS_KEY=your-aws-secret-access-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=your-s3-bucket-name

# Google Gemini AI Configuration
GEMINI_API_KEY=your-google-gemini-api-key
GEMINI_MODEL=gemini-1.5-flash
GEMINI_TEMPERATURE=0.7
GEMINI_TOP_P=0.8
GEMINI_TOP_K=40
GEMINI_MAX_TOKENS=2048

# Email Configuration (SMTP)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
EMAIL_FROM_NAME=Blog Platform
EMAIL_FROM_ADDRESS=your-email@gmail.com
FRONTEND_URL=http://localhost:4200
RESET_TOKEN_EXPIRE_MINUTES=15
EMAIL_VERIFICATION_TOKEN_EXPIRE_MINUTES=1440

# CORS Configuration
CORS_ORIGINS=http://localhost:4200,http://127.0.0.1:4200

# Environment
ENVIRONMENT=development
```

### Configuration Classes

```python
# app/core/config.py
from dataclasses import dataclass
from decouple import config

@dataclass
class Settings:
    # Database
    MONGODB_URL: str = config("MONGODB_URL")
    
    # Auth
    SECRET_KEY: str = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config("ACCESS_TOKEN_EXPIRE_MINUTES", default=30, cast=int)
    
    # AWS
    AWS_ACCESS_KEY: str = config("AWS_ACCESS_KEY_ID")
    AWS_SECRET_KEY: str = config("AWS_SECRET_ACCESS_KEY")
    
    # AI
    GEMINI_API_KEY: str = config("GEMINI_API_KEY")
```

## 📊 API Documentation

### Interactive Documentation

Once the server is running, access the auto-generated documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### Core API Endpoints

#### 🔐 Authentication

```http
POST   /api/v1/auth/register       # User registration
POST   /api/v1/auth/login          # User login
POST   /api/v1/auth/refresh        # Token refresh
POST   /api/v1/auth/logout         # User logout
GET    /api/v1/auth/me             # Current user profile
PUT    /api/v1/auth/update-username     # Update username
PUT    /api/v1/auth/update-profile-picture # Update profile picture
POST   /api/v1/auth/change-password     # Change password
POST   /api/v1/auth/forgot-password     # Request password reset
POST   /api/v1/auth/reset-password      # Reset password with token
POST   /api/v1/auth/verify-email        # Verify email address
POST   /api/v1/auth/resend-verification # Resend verification email
GET    /api/v1/auth/users/{user_id}     # Get public user profile
```

#### 📝 Blog Management

```http
GET    /api/v1/blogs/              # Get all blogs (paginated)
POST   /api/v1/blogs/              # Create new blog
GET    /api/v1/blogs/{id}          # Get specific blog
PUT    /api/v1/blogs/{id}          # Update blog
DELETE /api/v1/blogs/{id}          # Delete blog
GET    /api/v1/blogs/my-blogs      # Get user's blogs
GET    /api/v1/blogs/search/{query} # Search blogs
```

#### 💬 Social Features

```http
# Comments
POST   /api/v1/comments/blogs/{blog_id}     # Add comment
GET    /api/v1/comments/blogs/{blog_id}     # Get comments
DELETE /api/v1/comments/{comment_id}       # Delete comment

# Likes
POST   /api/v1/likes/blogs/{blog_id}        # Like/dislike blog
GET    /api/v1/likes/blogs/{blog_id}/count  # Get like count
DELETE /api/v1/likes/blogs/{blog_id}       # Remove like
```

#### 🏷️ Content Organization

```http
# Tags
GET    /api/v1/tags/                # Get all tags
POST   /api/v1/tags/                # Create tag
GET    /api/v1/tags/popular/        # Get popular tags
GET    /api/v1/tags/search/{query}  # Search tags

# Images
POST   /api/v1/images/blogs/{blog_id}  # Upload images
GET    /api/v1/images/blogs/{blog_id}  # Get blog images
DELETE /api/v1/images/blogs/{blog_id} # Delete images
```

#### 🤖 AI Features

```http
# AI Summarization
POST   /api/v1/summaries/           # Generate intelligent blog summary

# User Interests (for ML recommendations)
GET    /api/v1/interests/           # Get user interests
POST   /api/v1/interests/           # Set user interests
PUT    /api/v1/interests/           # Update interests
```

### Request/Response Examples

#### User Registration

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "secure_password123"
}

# Response
{
  "message": "Registration successful! Please check your email to verify your account before logging in.",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "username": "john_doe",
    "email": "john@example.com",
    "email_verified": false
  }
}
```

#### Create Blog Post

```http
POST /api/v1/blogs/
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
Content-Type: application/json

{
  "title": "Getting Started with FastAPI",
  "content": "[{\"id\":\"block_1\",\"type\":\"content\",\"data\":\"FastAPI is amazing...\"}]",
  "tags": ["python", "fastapi", "tutorial"],
  "main_image_url": "https://example.com/image.jpg",
  "published": true
}

# Response
{
  "id": "507f1f77bcf86cd799439012",
  "user_id": "507f1f77bcf86cd799439011",
  "username": "john_doe",
  "title": "Getting Started with FastAPI",
  "content": "[{\"id\":\"block_1\",\"type\":\"content\",\"data\":\"FastAPI is amazing...\"}]",
  "tags": ["python", "fastapi", "tutorial"],
  "main_image_url": "https://example.com/image.jpg",
  "published": true,
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": "2024-01-15T10:35:00Z",
  "comment_count": 0,
  "likes_count": 0
}
```

## 🤖 AI Integration

### Google Gemini AI Service

```python
# app/services/ai_summary.py
class AIService:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self.generation_config = {
            "temperature": 0.7,
            "top_p": 0.8,
            "top_k": 40,
            "max_output_tokens": 150
        }
    
    def extract_text_from_blog_content(self, content: str) -> str:
        """Extract plain text from structured blog content (JSON)"""
        # Handles JSON blocks, removes HTML tags, processes lists
        # Returns clean text for AI processing
    
    async def generate_summary(self, blog_content: str, blog_title: str) -> str:
        """Generate intelligent AI-powered summary using Gemini"""
        text_content = self.extract_text_from_blog_content(blog_content)
        prompt = f"""
Please provide a concise summary of the following blog post in 2-3 sentences.
Focus on the main points and key takeaways.

Title: {blog_title}
Content: {text_content}

Summary:
"""
        response = self.model.generate_content(prompt, generation_config=self.generation_config)
        return response.text.strip()
```

### Advanced ML Recommendation Engine

```python
# app/services/recommendation_service.py
class BlogRecommendationService:
    def __init__(self):
        self.stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            # ... comprehensive stop words list
        }
    
    def preprocess_text(self, text: str) -> str:
        """Advanced text preprocessing with stop-word removal"""
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)  # Remove special chars
        words = [word for word in text.split() 
                if word not in self.stop_words and len(word) > 2]
        return ' '.join(words)
    
    def calculate_content_similarity(self, user_interests: List[str], 
                                   blog_content: str, blog_title: str, 
                                   blog_tags: List[str]) -> float:
        """Advanced similarity calculation with weighted content"""
        user_profile = ' '.join(user_interests)
        
        # Weight title and tags more heavily
        blog_document = f"{blog_title} {blog_title} {blog_content} {' '.join(blog_tags)} {' '.join(blog_tags)}"
        
        # Preprocess both documents
        user_profile_clean = self.preprocess_text(user_profile)
        blog_document_clean = self.preprocess_text(blog_document)
        
        vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),  # Unigrams and bigrams
            min_df=1,
            max_df=0.8
        )
        
        documents = [user_profile_clean, blog_document_clean]
        tfidf_matrix = vectorizer.fit_transform(documents)
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        
        return float(similarity)
    
    def calculate_engagement_score(self, blog: dict) -> float:
        """Multi-factor engagement scoring"""
        score = 0.0
        
        # Recency bonus
        days_old = (datetime.now() - blog.get('created_at', datetime.now())).days
        if days_old < 1: score += 0.3
        elif days_old < 7: score += 0.2
        elif days_old < 30: score += 0.1
        
        # Published status and likes
        if blog.get('published', False): score += 0.2
        score += min(blog.get("likes_count", 0) * 0.01, 0.3)
        
        return min(score, 1.0)
```

## 📧 Email System

### Professional Email Templates

The backend includes a comprehensive email system with modern, responsive HTML templates:

```python
# app/services/email_service.py
class EmailService:
    async def send_email_verification_email(self, to_email: str, verification_token: str):
        """Send beautiful email verification with professional template"""
        verification_link = f"{settings.FRONTEND_URL}/auth/verify-email?token={verification_token}"
        html_template = get_email_verification_template(verification_link)
        return await self.send_email(to_email, "Verify Your Email", html_template, is_html=True)
    
    async def send_password_reset_email(self, to_email: str, reset_token: str):
        """Send password reset email with secure token"""
        reset_link = f"{settings.FRONTEND_URL}/auth/reset-password?token={reset_token}"
        html_template = get_password_reset_email_template(reset_link)
        return await self.send_email(to_email, "Password Reset Request", html_template, is_html=True)
```

### Email Features

- **Responsive Design**: Mobile-friendly HTML templates with gradient headers
- **Security Tokens**: Secure token generation with expiration times
- **Professional Styling**: Modern dark theme matching the application design
- **Fallback Support**: Plain text versions for all HTML emails
- **SMTP Integration**: Support for Gmail, Outlook, and custom SMTP servers

### Email Verification Flow

1. **Registration**: User registers, email verification token generated
2. **Email Sent**: Professional verification email with secure link
3. **Verification**: User clicks link, email verified, account activated
4. **Confirmation**: Success email sent confirming verification

### Password Reset Flow

1. **Request**: User requests password reset
2. **Token Generation**: Secure reset token created (15-minute expiry)
3. **Email Delivery**: Professional reset email with secure link
4. **Reset**: User resets password, token invalidated
5. **Confirmation**: Success email confirming password change

## 🔒 Security

### Authentication System

#### JWT Token Management

```python
# app/core/auth.py
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
```

#### Password Security

```python
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
```

### Security Best Practices

- ✅ **Input Validation**: Comprehensive validation with Pydantic models
- ✅ **Email Verification**: Mandatory email verification before account access
- ✅ **Token Security**: Secure token generation with hashing and expiration
- ✅ **Password Security**: Bcrypt hashing with salt, secure reset flow
- ✅ **SQL Injection Prevention**: MongoDB with proper query building
- ✅ **XSS Protection**: Content sanitization and validation
- ✅ **CORS Configuration**: Configurable origin allowlist
- ✅ **Cookie Security**: HTTP-only, secure, SameSite cookie configuration
- ✅ **Token Rotation**: Automatic refresh token rotation and invalidation

### Environment-Specific Security

```python
# Production security settings
class ProductionSettings(Settings):
    CORS_ORIGINS = ["https://yourdomain.com"]
    COOKIE_SECURE = True
    COOKIE_SAMESITE = "strict"
    COOKIE_HTTPONLY = True
```

## 🧪 Testing

### Setup Test Environment

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx pytest-cov

# Create test database
export MONGODB_URL="mongodb://localhost:27017/blog_test"
```

### Run Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth.py -v

# Run with verbose output
pytest -v -s
```

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Test configuration
├── test_auth.py            # Authentication tests
├── test_blogs.py           # Blog CRUD tests
├── test_comments.py        # Comment system tests
├── test_likes.py           # Like functionality tests
├── test_recommendations.py # ML recommendation tests
└── test_ai_service.py      # AI integration tests
```

### Example Test

```python
# tests/test_auth.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_user_registration():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/api/v1/auth/register", json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword123"
        })
    
    assert response.status_code == 201
    data = response.json()
    assert "access_token" in data
    assert data["user"]["username"] == "testuser"
```

## 🚀 Deployment

### Production Deployment

#### Using Gunicorn (Recommended)

```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# With configuration file
gunicorn main:app -c gunicorn.conf.py
```

#### Gunicorn Configuration

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "uvicorn.workers.UvicornWorker"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
keepalive = 2
```

### Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run application
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

#### Build and Run

```bash
# Build image
docker build -t blogplatform-backend .

# Run container
docker run -d \
  --name blogplatform-api \
  -p 8000:8000 \
  --env-file .env \
  blogplatform-backend

# Check logs
docker logs blogplatform-api
```

### Cloud Deployment

#### Heroku

```bash
# Create Procfile
echo "web: gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:\$PORT" > Procfile

# Deploy to Heroku
heroku create your-app-name
heroku config:set MONGODB_URL="your-mongodb-url"
heroku config:set SECRET_KEY="your-secret-key"
git push heroku main
```

#### AWS ECS

```json
{
  "family": "blogplatform-backend",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "backend",
      "image": "your-account.dkr.ecr.region.amazonaws.com/blogplatform-backend:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "production"
        }
      ]
    }
  ]
}
```

### Performance Monitoring

```python
# Add to main.py for production monitoring
import time
from fastapi import Request

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 🤝 Contributing

### Development Setup

```bash
# Fork and clone
git clone https://github.com/yourusername/BlogPlatform.git
cd BlogPlatform/backend

# Create feature branch
git checkout -b feature/amazing-feature

# Install development dependencies
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
flake8 .
mypy .

# Run tests
pytest --cov=app
```

### Commit Guidelines

```bash
# Commit format
git commit -m "feat(auth): add social login with Google OAuth

Implemented Google OAuth integration for faster user onboarding.
Includes proper error handling and token management.

Closes #123"
```

### Pull Request Process

1. **Update Documentation**: Update README if needed
2. **Add Tests**: Ensure new features have tests
3. **Code Quality**: Pass all linting and formatting checks
4. **Performance**: No significant performance degradation
5. **Security**: No security vulnerabilities introduced

---

## 🚀 Recent Updates

### v2.0.0 - Enhanced Email & AI Features
- ✨ **Professional Email System**: Beautiful HTML templates with responsive design
- 🔐 **Enhanced Security**: Mandatory email verification, secure password reset
- 🤖 **Advanced AI**: Intelligent blog summarization with Google Gemini 1.5
- 📈 **Improved ML**: Enhanced recommendation engine with advanced text processing
- 👤 **User Profiles**: Profile picture management and enhanced user features
- 🎨 **Professional Templates**: Modern email designs matching application theme

---

⭐ **Star this repo if you find it helpful!**

Built with ❤️ and ☕ by the BlogPlatform Backend Team

