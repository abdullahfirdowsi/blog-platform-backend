from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection
from routers import auth, blogs, comments, likes, tags, images, interests

from routers.auth import router as auth_router
from routers.blogs import router as blogs_router
from routers.comments import router as comments_router
from routers.likes import router as likes_router
from routers.tags import router as tags_router
from routers.images import router as images_router
from routers.interests import router as interests_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await connect_to_mongo()
    yield
    # Shutdown
    await close_mongo_connection()

app = FastAPI(
    title="Blog Platform API",
    description="A comprehensive blogging platform with user authentication, blog management, comments, likes, and tags",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular development server
        "http://127.0.0.1:4200",  # Alternative localhost
        "http://localhost:3000",  # In case you switch to React
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
    allow_headers=[
        "Authorization", 
        "Content-Type", 
        "Accept", 
        "Origin", 
        "X-Requested-With",
        "Access-Control-Request-Method",
        "Access-Control-Request-Headers",
        "Cross-Origin-Opener-Policy",
        "Cross-Origin-Embedder-Policy"
    ],
    expose_headers=[
        "Set-Cookie",
        "Cross-Origin-Opener-Policy",
        "Cross-Origin-Embedder-Policy"
    ]
)

# Add custom middleware for Google OAuth headers
@app.middleware("http")
async def add_oauth_headers(request, call_next):
    response = await call_next(request)
    
    # Add headers needed for Google OAuth
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin-allow-popups"
    response.headers["Cross-Origin-Embedder-Policy"] = "unsafe-none"
    
    return response

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(blogs_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(likes_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")
app.include_router(interests_router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Blog Platform API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

