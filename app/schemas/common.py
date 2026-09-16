from pydantic import BaseModel
from typing import Generic, TypeVar


T = TypeVar("T")


class ErrorResponse(BaseModel):
    detail: str
    code: str


class Paginated(BaseModel, Generic[T]):
    items: list[T]
    total: int
    page: int
    page_size: int
