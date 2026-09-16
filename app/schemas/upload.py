from pydantic import BaseModel
from typing import Optional


class PresignRequest(BaseModel):
    filename: str
    content_type: str


class PresignResponse(BaseModel):
    upload_url: str
    public_url: str
    key: str


class UploadResponse(BaseModel):
    public_url: str
