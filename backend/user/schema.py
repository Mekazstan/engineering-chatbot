from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field
from db.models import UserPlan, SubscriptionStatus, InvoiceStatus

# --------------------------
# User Profile Schemas
# --------------------------

class UserProfileBase(BaseModel):
    name: Optional[str] = None
    company: Optional[str] = None
    job_title: Optional[str] = None
    phone: Optional[str] = None

class UserProfileUpdate(UserProfileBase):
    pass

class UserProfileResponse(UserProfileBase):
    user_id: int
    email: EmailStr
    avatar_url: Optional[str] = None
    plan: UserPlan
    plan_renewal_date: Optional[datetime] = None
    api_key: Optional[str] = None

class UsageStats(BaseModel):
    current: int
    limit: int
    percentage: float

class UserProfileWithUsageResponse(UserProfileResponse):
    usage: dict[str, UsageStats]  # queries, documents

class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)

class AvatarUploadResponse(BaseModel):
    avatar_url: str

class EmailPreferencesUpdate(BaseModel):
    updates: bool = True
    tips: bool = True
    security: bool = True
    newsletter: bool = True

class APIKeyResponse(BaseModel):
    api_key: str

# --------------------------
# Subscription & Billing Schemas
# --------------------------

class SubscriptionUpgrade(BaseModel):
    plan: UserPlan = UserPlan.PRO
    payment_method_id: str

class SubscriptionResponse(BaseModel):
    subscription_id: int
    plan: UserPlan
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime

class SubscriptionCancelResponse(BaseModel):
    message: str
    end_date: datetime

class InvoiceResponse(BaseModel):
    invoice_id: int
    amount: int
    currency: str
    status: InvoiceStatus
    date: datetime
    description: Optional[str] = None
    pdf_url: Optional[str] = None

class BillingHistoryResponse(BaseModel):
    invoices: List[InvoiceResponse]