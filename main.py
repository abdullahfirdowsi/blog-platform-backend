from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pydantic import ValidationError

from app.db.database import connect_to_mongo, close_mongo_connection
from app.core.config import settings

# Import API routers
from app.routers.auth import router as auth_router
from app.routers.blogs import router as blogs_router
from app.routers.comments import router as comments_router
from app.routers.likes import router as likes_router
from app.routers.tags import router as tags_router
from app.routers.interests import router as interests_router
from app.routers.images import router as images_router
from app.routers.summaries import router as summaries_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Blog Platform API",
    description="A comprehensive blogging platform with user authentication, blog management, comments, likes, and tags.",
    version="1.0.0",
    lifespan=lifespan
)

# Custom exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors to provide better error messages
    """
    import logging
    logger = logging.getLogger(__name__)
    
    # Log the original error for debugging
    logger.info(f"Validation error: {exc.errors()}")
    
    errors = []
    for error in exc.errors():
        field_name = error["loc"][-1] if error["loc"] else "field"
        error_type = error["type"]
        error_msg = error.get("msg", "")
        
        # Log individual error details for debugging
        logger.info(f"Field: {field_name}, Type: {error_type}, Message: {error_msg}")
        
        # Customize email validation error messages
        if (field_name == "email" and (
            error_type == "value_error" or
            error_type in ["value_error.email", "string_type", "type_error.str"] or
            "email" in error_type.lower() or
            any(keyword in error_msg.lower() for keyword in ["email", "valid", "@-sign", "@"])
        )):
            errors.append({
                "field": field_name,
                "message": "Please enter a valid email address (e.g., user@example.com)"
            })
        # Handle other email fields
        elif "email" in field_name.lower() and (
            error_type in ["value_error.email", "string_type", "type_error.str"] or
            "email" in error_type.lower() or
            "valid" in error_msg.lower()
        ):
            errors.append({
                "field": field_name,
                "message": f"Invalid email format for {field_name}"
            })
        # Customize other validation errors
        elif error_type == "missing":
            errors.append({
                "field": field_name,
                "message": f"{field_name.title()} is required"
            })
        elif error_type in ["value_error.any_str.min_length", "string_too_short"]:
            min_length = error.get("ctx", {}).get("limit_value", error.get("ctx", {}).get("min_length", "required"))
            if field_name == "password":
                errors.append({
                    "field": field_name,
                    "message": f"Password must be at least {min_length} characters long"
                })
            elif field_name == "username":
                errors.append({
                    "field": field_name,
                    "message": f"Username must be at least {min_length} characters long"
                })
            else:
                errors.append({
                    "field": field_name,
                    "message": f"{field_name.title()} must be at least {min_length} characters long"
                })
        elif error_type == "value_error":
            # Handle custom validation errors (like username with spaces)
            if "Username cannot contain spaces" in error_msg:
                errors.append({
                    "field": field_name,
                    "message": "Username cannot contain spaces"
                })
            else:
                errors.append({
                    "field": field_name,
                    "message": error_msg or f"Invalid value for {field_name}"
                })
        else:
            # Default error message - try to extract meaningful message
            message = error_msg
            if not message or "value is not a valid" in message.lower():
                if field_name == "email":
                    message = "Please enter a valid email address (e.g., user@example.com)"
                else:
                    message = f"Invalid value for {field_name}"
            
            errors.append({
                "field": field_name,
                "message": message
            })
    
    # Return the first error message as the main detail for backward compatibility
    detail = errors[0]["message"] if errors else "Validation error"
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": detail,
            "errors": errors
        }
    )

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200","http://127.0.0.1:4200","https://blogplatformapplicationilink.netlify.app"],  # Read from .env
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register Routers
api_prefix = "/api/v1"
app.include_router(auth_router, prefix=api_prefix, tags=["Auth"])
app.include_router(blogs_router, prefix=api_prefix, tags=["Blogs"])
app.include_router(images_router, prefix=api_prefix, tags=["Images"])
app.include_router(comments_router, prefix=api_prefix, tags=["Comments"])
app.include_router(likes_router, prefix=api_prefix, tags=["Likes"])
app.include_router(tags_router, prefix=api_prefix, tags=["Tags"])
app.include_router(interests_router, prefix=api_prefix, tags=["Interests"])
app.include_router(summaries_router, prefix=api_prefix, tags=["Summaries"])

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
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
