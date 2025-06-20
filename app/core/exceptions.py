import logging
from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    Custom handler for Pydantic validation errors to provide better error messages
    """
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

