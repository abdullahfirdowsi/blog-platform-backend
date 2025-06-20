from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager

from app.db.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings
from app.core.exceptions import validation_exception_handler

# Import API routers
from app.routers.auth import router as auth_router
from app.routers.blogs import router as blogs_router
from app.routers.comments import router as comments_router
from app.routers.likes import router as likes_router
from app.routers.tags import router as tags_router
from app.routers.interests import router as interests_router
from app.routers.images import router as images_router
from app.routers.summaries import router as summaries_router
from app.routers.dashboard import router as dashboard_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Blog Platform API",
    description="A comprehensive blogging platform with user authentication, blog management, comments, likes, and tags.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    root_path="",
    redirect_slashes=False,  # Disable automatic slash redirects
    openapi_prefix=""  # Ensure OpenAPI schema uses correct paths
)

# Add trusted host middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Base middleware for consistent route handling
@app.middleware("http")
async def route_handler_middleware(request: Request, call_next):
    # Don't modify paths for OpenAPI documentation
    if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
        return await call_next(request)
    
    path = request.url.path
    original_path = path
    
    # Handle trailing slashes more gracefully
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/")
        # Only modify if it's an API endpoint
        if path.startswith("/api/"):
            request.scope["path"] = path
    
    # Ensure the scheme is properly set
    if "x-forwarded-proto" in request.headers:
        request.scope["scheme"] = request.headers["x-forwarded-proto"]
    elif "x-scheme" in request.headers:
        request.scope["scheme"] = request.headers["x-scheme"]
    
    response = await call_next(request)
    
    # If we get a 404 and we modified the path, try the original path
    if response.status_code == 404 and original_path != path:
        request.scope["path"] = original_path
        response = await call_next(request)
    
    return response

# Register custom exception handler for validation errors
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Temporarily allowing all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix)
app.include_router(blogs_router, prefix=api_prefix)
app.include_router(images_router, prefix=api_prefix)
app.include_router(comments_router, prefix=api_prefix)
app.include_router(likes_router, prefix=api_prefix)
app.include_router(tags_router, prefix=api_prefix)
app.include_router(interests_router, prefix=api_prefix)
app.include_router(summaries_router, prefix=api_prefix)
app.include_router(dashboard_router, prefix=api_prefix)

# Root and Health Endpoints
@app.get("/", tags=["Root"])
async def root():
    return {"message": "Hello from FastAPI!"}

@app.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


# Development server runner
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        forwarded_allow_ips="*",
        proxy_headers=True,
        server_header=False
    )
