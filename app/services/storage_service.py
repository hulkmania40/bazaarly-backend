import uuid
from app.core.config import settings


class StorageService:
    @staticmethod
    def presign(filename: str, content_type: str) -> dict:
        key = f"uploads/{uuid.uuid4()}_{filename}"
        return {
            "upload_url": f"https://{settings.s3_bucket}.s3.{settings.s3_region}.amazonaws.com/{key}",
            "public_url": f"https://{settings.s3_bucket}.s3.{settings.s3_region}.amazonaws.com/{key}",
            "key": key,
        }
