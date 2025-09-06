"""
ICRA Database Models

SQLAlchemy models for the Interactive Code Review Agent database.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

Base = declarative_base()

class Review(Base):
    """Code review model"""
    __tablename__ = "reviews"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    repository_url = Column(String, nullable=False)
    pull_request_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    author_id = Column(String, nullable=False)
    reviewer_id = Column(String)
    status = Column(String, default="pending")  # pending, in_progress, approved, rejected
    priority = Column(String, default="medium")  # low, medium, high, critical
    security_score = Column(Integer)
    files_changed = Column(Integer, default=0)
    lines_added = Column(Integer, default=0)
    lines_removed = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    approved_at = Column(DateTime)
    approved_by = Column(String)
    rejected_at = Column(DateTime)
    rejected_by = Column(String)
    rejection_reason = Column(Text)
    
    # Relationships
    comments = relationship("Comment", back_populates="review", cascade="all, delete-orphan")
    security_findings = relationship("SecurityFinding", back_populates="review", cascade="all, delete-orphan")
    file_changes = relationship("FileChange", back_populates="review", cascade="all, delete-orphan")

class Comment(Base):
    """Review comment model"""
    __tablename__ = "comments"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    user_id = Column(String, nullable=False)
    user_name = Column(String, nullable=False)
    text = Column(Text, nullable=False)
    file_path = Column(String)
    line_number = Column(Integer)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    resolved = Column(Boolean, default=False)
    resolved_by = Column(String)
    resolved_at = Column(DateTime)
    
    # Relationships
    review = relationship("Review", back_populates="comments")

class SecurityFinding(Base):
    """Security vulnerability finding model"""
    __tablename__ = "security_findings"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    finding_type = Column(String, nullable=False)  # SQL_INJECTION, XSS, etc.
    severity = Column(String, nullable=False)  # low, medium, high, critical
    file_path = Column(String, nullable=False)
    line_number = Column(Integer)
    description = Column(Text, nullable=False)
    recommendation = Column(Text)
    cve_id = Column(String)
    confidence_score = Column(Float)
    status = Column(String, default="open")  # open, fixed, false_positive, accepted
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="security_findings")

class FileChange(Base):
    """File change model for tracking modified files in reviews"""
    __tablename__ = "file_changes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    file_path = Column(String, nullable=False)
    change_type = Column(String, nullable=False)  # added, modified, deleted
    lines_added = Column(Integer, default=0)
    lines_removed = Column(Integer, default=0)
    old_content = Column(Text)
    new_content = Column(Text)
    diff_content = Column(Text)
    created_at = Column(DateTime, default=func.now())
    
    # Relationships
    review = relationship("Review", back_populates="file_changes")

class User(Base):
    """User model for collaboration features"""
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    avatar_url = Column(String)
    role = Column(String, default="developer")  # developer, reviewer, admin
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class CollaborationSession(Base):
    """Real-time collaboration session model"""
    __tablename__ = "collaboration_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    user_id = Column(String, nullable=False)
    session_token = Column(String, unique=True, nullable=False)
    status = Column(String, default="active")  # active, inactive, disconnected
    joined_at = Column(DateTime, default=func.now())
    last_activity = Column(DateTime, default=func.now())
    disconnected_at = Column(DateTime)

class ReviewMetrics(Base):
    """Review metrics and analytics model"""
    __tablename__ = "review_metrics"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    review_id = Column(String, ForeignKey("reviews.id"), nullable=False)
    metric_name = Column(String, nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String)
    calculated_at = Column(DateTime, default=func.now())
    
    # Common metrics: review_time, code_quality_score, complexity_score, etc.
