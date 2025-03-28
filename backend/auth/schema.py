from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from db.models import UserPlan, UserStatus, UserRole

# --------------------------
# Shared Base Schemas
# --------------------------

class TimestampMixin(BaseModel):
    created_at: datetime
    updated_at: datetime

class Pagination(BaseModel):
    total: int
    limit: int
    offset: int

# --------------------------
# Authentication Schemas
# --------------------------

class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    plan: UserPlan = UserPlan.FREE

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserGoogleAuth(BaseModel):
    token: str

class PasswordResetRequest(BaseModel):
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(UserBase):
    user_id: int
    plan: UserPlan
    role: UserRole
    status: UserStatus
    api_key: Optional[str] = None

