from fastapi import APIRouter, Depends
from app.core.deps import require_role
from app.services.storage_service import StorageService
from app.schemas.upload import PresignResponse, UploadResponse

router = APIRouter()


@router.post("/uploads/presign")
async def presign(data: dict, _=Depends(require_role("seller"))):
    result = StorageService.presign(data["filename"], data["content_type"])
    return PresignResponse(**result)


@router.post("/uploads", response_model=UploadResponse)
async def upload_file(_=Depends(require_role("seller"))):
    return UploadResponse(public_url="https://example.com/uploaded-file.jpg")
