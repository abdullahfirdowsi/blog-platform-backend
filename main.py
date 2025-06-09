from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from database import connect_to_mongo, close_mongo_connection

from routers.auth import router as auth_router
from routers.blogs import router as blogs_router
from routers.comments import router as comments_router
from routers.likes import router as likes_router
from routers.tags import router as tags_router
from routers.interests import router as interests_router
from routers.images import router as images_router

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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(blogs_router, prefix="/api/v1")
app.include_router(images_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(likes_router, prefix="/api/v1")
app.include_router(tags_router, prefix="/api/v1")
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

