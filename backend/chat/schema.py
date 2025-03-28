from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
from auth.schema import TimestampMixin, Pagination

# --------------------------
# Chat Schemas
# --------------------------

class MessageBase(BaseModel):
    content: str
    role: str  # user/assistant

class MessageCreate(BaseModel):
    query: str
    document_ids: Optional[List[int]] = None
    conversation_id: Optional[int] = None

class MessageResponse(MessageBase):
    message_id: int
    conversation_id: int
    timestamp: datetime
    is_off_topic: bool = False

class MessageSourceResponse(BaseModel):
    source_id: int
    document_id: int
    document_name: str
    page: int
    text: str
    relevance_score: float

class ChatResponse(BaseModel):
    message_id: int
    conversation_id: int
    response: str
    sources: List[MessageSourceResponse]
    is_off_topic: bool

class ConversationBase(BaseModel):
    pass

class ConversationResponse(TimestampMixin):
    conversation_id: int
    user_id: int
    messages: List[MessageResponse]

class ConversationListResponse(BaseModel):
    conversations: List[dict]  # Simplified conversation objects
    pagination: Pagination

class ScreenshotUploadResponse(BaseModel):
    screenshot_id: int
    url: str
    text_content: Optional[str] = None