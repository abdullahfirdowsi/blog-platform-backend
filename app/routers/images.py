import logging
from uuid import uuid4
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from decouple import config

from app.models.models import SingleImageResponse, S3ImagesListResponse
from app.core.auth import get_current_user

router = APIRouter(prefix="/images", tags=["Images"])

# AWS Configuration
AWS_ACCESS_KEY = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION", default="eu-north-1")
BUCKET_NAME = config("S3_BUCKET_NAME", default="blog-app-2025")
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

# S3 Client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

# Logger Setup
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


def generate_s3_url(key: str) -> str:
    """Generate a public URL for a given S3 key."""
    base = f"https://{BUCKET_NAME}.s3"
    return (
        f"{base}.{AWS_REGION}.amazonaws.com/{key}"
        if AWS_REGION != "us-east-1"
        else f"{base}.amazonaws.com/{key}"
    )


@router.post("/upload", response_model=SingleImageResponse)
async def upload_image(
    image: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Upload a validated image to AWS S3."""
    try:
        if not image.content_type or not image.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="Only image files are allowed")

        contents = await image.read()
        if not contents:
            raise HTTPException(status_code=400, detail="File is empty")
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(status_code=413, detail="File exceeds 5MB limit")

        file_ext = image.filename.split('.')[-1] if '.' in image.filename else 'jpg'
        key = f"uploads/{uuid4().hex}.{file_ext}"

        try:
            s3_client.upload_fileobj(
                Fileobj=BytesIO(contents),
                Bucket=BUCKET_NAME,
                Key=key,
                ExtraArgs={
                    "ContentType": image.content_type,
                    "ACL": "public-read"
                }
            )
        except ClientError as e:
            if "AccessControlListNotSupported" in str(e):
                s3_client.upload_fileobj(
                    Fileobj=BytesIO(contents),
                    Bucket=BUCKET_NAME,
                    Key=key,
                    ExtraArgs={"ContentType": image.content_type}
                )
            else:
                logger.error(f"Upload failed: {e}")
                raise HTTPException(status_code=500, detail="Upload to S3 failed")

        s3_client.head_object(Bucket=BUCKET_NAME, Key=key)
        return SingleImageResponse(
            success=True,
            message="Image uploaded successfully",
            imageUrl=generate_s3_url(key)
        )

    except ClientError as ce:
        logger.error(f"S3 ClientError: {ce}")
        raise HTTPException(status_code=500, detail="S3 client error")
    except Exception as e:
        logger.exception("Unexpected upload error")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/list", response_model=S3ImagesListResponse)
async def list_images(
    prefix: str = "uploads/",
    current_user: dict = Depends(get_current_user)
):
    """List uploaded images in the S3 bucket."""
    try:
        response = s3_client.list_objects_v2(Bucket=BUCKET_NAME, Prefix=prefix)
        items = response.get("Contents", [])
        images = [
            {
                "key": obj["Key"],
                "url": generate_s3_url(obj["Key"]),
                "size": obj["Size"],
                "lastModified": obj["LastModified"].isoformat()
            }
            for obj in items
        ]
        return S3ImagesListResponse(success=True, images=images)
    except ClientError as e:
        logger.error(f"S3 list error: {e}")
        raise HTTPException(status_code=500, detail="Error listing images")


@router.get("/{file_key:path}", response_model=SingleImageResponse)
async def get_image_url(
    file_key: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a presigned URL for the image."""
    try:
        s3_client.head_object(Bucket=BUCKET_NAME, Key=file_key)
        url = s3_client.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": BUCKET_NAME, "Key": file_key},
            ExpiresIn=3600  # 1 hour
        )
        return SingleImageResponse(success=True, imageUrl=url)
    except ClientError as e:
        if e.response["Error"]["Code"] == "404":
            raise HTTPException(status_code=404, detail="Image not found")
        logger.error(f"Presign error: {e}")
        raise HTTPException(status_code=500, detail="Error generating URL")
