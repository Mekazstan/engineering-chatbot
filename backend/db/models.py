from datetime import datetime
from enum import Enum
from sqlalchemy import (Column, String, Integer, ForeignKey, DateTime, Boolean, Float,
    Enum as SQLEnum, Text
)
from sqlalchemy.orm import relationship
from .main import Base
import uuid


# Enums for status fields
class UserStatus(str, Enum):
    ACTIVE = "active"
    BANNED = "banned"

class UserRole(str, Enum):
    USER = "user"
    ADMIN = "admin"

class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    UNPAID = "unpaid"

class InvoiceStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    PAID = "paid"
    VOID = "void"
    
class UserPlan(str, Enum):
    FREE = "free"
    PRO = "pro"

class User(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key=True, default=uuid.uuid4)
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=True)
    company = Column(String(100))
    job_title = Column(String(100))
    phone = Column(String(20))
    avatar_url = Column(String(255))
    plan = Column(SQLEnum(UserPlan), default=UserPlan.FREE)
    plan_renewal_date = Column(DateTime)
    api_key = Column(String(100), unique=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER)
    status = Column(SQLEnum(UserStatus), default=UserStatus.ACTIVE)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    documents = relationship("Document", back_populates="user")
    conversations = relationship("Conversation", back_populates="user")
    email_preferences = relationship("EmailPreferences", back_populates="user", uselist=False)
    subscriptions = relationship("Subscription", back_populates="user")
    invoices = relationship("Invoice", back_populates="user")

class Document(Base):
    __tablename__ = "documents"
    
    document_id = Column(Integer, primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    name = Column(String(255), nullable=False)
    size = Column(Integer)  # in bytes
    file_type = Column(String(50))
    s3_url = Column(String(512))
    status = Column(SQLEnum(DocumentStatus), default=DocumentStatus.UPLOADED)
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_date = Column(DateTime)
    pages = Column(Integer)
    
    # Relationships
    user = relationship("User", back_populates="documents")
    message_sources = relationship("MessageSources", back_populates="document")

class Conversation(Base):
    __tablename__ = "conversations"
    
    conversation_id = Column(Integer, primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    
    message_id = Column(Integer, primary_key=True, default=uuid.uuid4)
    conversation_id = Column(Integer, ForeignKey("conversations.conversation_id"), nullable=False)
    role = Column(String(20))  # user/assistant
    content = Column(Text, nullable=False)
    is_off_topic = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sources = relationship("MessageSources", back_populates="message")

class MessageSources(Base):
    __tablename__ = "message_sources"
    
    source_id = Column(Integer, primary_key=True, default=uuid.uuid4)
    message_id = Column(Integer, ForeignKey("messages.message_id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.document_id"), nullable=False)
    page = Column(Integer)
    text = Column(Text)
    relevance_score = Column(Float)
    
    # Relationships
    message = relationship("Message", back_populates="sources")
    document = relationship("Document", back_populates="message_sources")

class EmailPreferences(Base):
    __tablename__ = "email_preferences"
    
    user_id = Column(Integer, ForeignKey("users.user_id"), primary_key=True)
    updates = Column(Boolean, default=True)
    tips = Column(Boolean, default=True)
    security = Column(Boolean, default=True)
    newsletter = Column(Boolean, default=True)
    
    # Relationships
    user = relationship("User", back_populates="email_preferences")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    subscription_id = Column(Integer, primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    plan = Column(String(50), nullable=False)
    status = Column(SQLEnum(SubscriptionStatus), nullable=False)
    current_period_start = Column(DateTime)
    current_period_end = Column(DateTime)
    stripe_subscription_id = Column(String(100), unique=True)
    
    # Relationships
    user = relationship("User", back_populates="subscriptions")

class Invoice(Base):
    __tablename__ = "invoices"
    
    invoice_id = Column(Integer, primary_key=True, default=uuid.uuid4)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    amount = Column(Integer, nullable=False)  # in cents
    currency = Column(String(3), default="USD")
    status = Column(SQLEnum(InvoiceStatus), nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
    description = Column(Text)
    stripe_invoice_id = Column(String(100), unique=True)
    pdf_url = Column(String(512))
    
    # Relationships
    user = relationship("User", back_populates="invoices")