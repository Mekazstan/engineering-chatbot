from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr
from db.models import UserPlan, UserStatus
from auth.schema import Pagination

# --------------------------
# Admin Schemas
# --------------------------

class AuditLogResponse(BaseModel):
    log_id: int
    timestamp: datetime
    user_id: int
    user_name: str
    user_email: str
    query: Optional[str] = None
    response: Optional[str] = None
    document_id: Optional[int] = None
    document_name: Optional[str] = None

class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    pagination: Pagination

class UserAdminResponse(BaseModel):
    user_id: int
    name: str
    email: EmailStr
    status: UserStatus
    plan: UserPlan
    queries: int
    documents: int
    last_active: Optional[datetime] = None
    created_at: datetime

class UserAdminListResponse(BaseModel):
    users: List[UserAdminResponse]
    pagination: Pagination

class UserStatusUpdate(BaseModel):
    status: UserStatus

class UserPlanUpdate(BaseModel):
    plan: UserPlan