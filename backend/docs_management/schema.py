from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from db.models import DocumentStatus
from auth.schema import TimestampMixin, Pagination

# --------------------------
# Document Schemas
# --------------------------

class DocumentBase(BaseModel):
    name: str
    size: Optional[int] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentResponse(DocumentBase, TimestampMixin):
    document_id: int
    user_id: int
    file_type: Optional[str] = None
    s3_url: Optional[str] = None
    status: DocumentStatus
    upload_date: datetime
    processed_date: Optional[datetime] = None
    pages: Optional[int] = None

class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    pagination: Pagination

class DocumentStatusResponse(BaseModel):
    document_id: int
    status: DocumentStatus
    progress: Optional[int] = Field(None, ge=0, le=100)
    message: Optional[str] = None