"""
ICRA Backend API - Main FastAPI Application

Interactive Code Review Agent REST API server.
Provides endpoints for code review operations, collaboration, and integration.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
import asyncio
import logging
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ICRA_API")

# FastAPI app instance
app = FastAPI(
    title="Interactive Code Review Agent (ICRA) API",
    description="AI-Powered Code Review with Real-time Collaboration",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests/responses
class ReviewRequest(BaseModel):
    repository_url: str
    pull_request_id: str
    reviewer_id: str
    priority: str = "medium"

class ReviewResponse(BaseModel):
    review_id: str
    status: str
    created_at: datetime
    estimated_completion: Optional[datetime] = None

class CommentRequest(BaseModel):
    review_id: str
    user_id: str
    text: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

class SecurityAnalysisResponse(BaseModel):
    review_id: str
    security_score: int
    vulnerabilities: List[Dict[str, Any]]
    recommendations: List[str]

# In-memory storage for demo (replace with database in production)
reviews_db = {}
comments_db = {}
users_db = {}

@app.get("/")
async def root():
    """Root endpoint - API health check"""
    return {
        "message": "ICRA API is running",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "api": "running",
            "database": "connected",
            "security_engine": "active"
        }
    }

@app.post("/reviews", response_model=ReviewResponse)
async def create_review(review_request: ReviewRequest, background_tasks: BackgroundTasks):
    """Create a new code review"""
    review_id = str(uuid.uuid4())
    
    review = {
        "id": review_id,
        "repository_url": review_request.repository_url,
        "pull_request_id": review_request.pull_request_id,
        "reviewer_id": review_request.reviewer_id,
        "priority": review_request.priority,
        "status": "pending",
        "created_at": datetime.now(),
        "updated_at": datetime.now(),
        "security_score": None,
        "files_analyzed": 0,
        "comments_count": 0
    }
    
    reviews_db[review_id] = review
    
    # Start background review process
    background_tasks.add_task(process_review, review_id)
    
    logger.info(f"Created new review: {review_id}")
    
    return ReviewResponse(
        review_id=review_id,
        status="pending",
        created_at=review["created_at"]
    )

@app.get("/reviews")
async def list_reviews(status: Optional[str] = None, limit: int = 10):
    """List all reviews with optional filtering"""
    reviews = list(reviews_db.values())
    
    if status:
        reviews = [r for r in reviews if r["status"] == status]
    
    # Sort by created_at descending
    reviews.sort(key=lambda x: x["created_at"], reverse=True)
    
    return {
        "reviews": reviews[:limit],
        "total": len(reviews),
        "filtered": len(reviews) if status else None
    }

@app.get("/reviews/{review_id}")
async def get_review(review_id: str):
    """Get detailed information about a specific review"""
    if review_id not in reviews_db:
        raise HTTPException(status_code=404, detail="Review not found")
    
    review = reviews_db[review_id]
    
    # Get associated comments
    review_comments = [c for c in comments_db.values() if c["review_id"] == review_id]
    
    return {
        "review": review,
        "comments": review_comments,
        "comment_count": len(review_comments)
    }

@app.post("/reviews/{review_id}/comments")
async def add_comment(review_id: str, comment_request: CommentRequest):
    """Add a comment to a review"""
    if review_id not in reviews_db:
        raise HTTPException(status_code=404, detail="Review not found")
    
    comment_id = str(uuid.uuid4())
    comment = {
        "id": comment_id,
        "review_id": review_id,
        "user_id": comment_request.user_id,
        "text": comment_request.text,
        "file_path": comment_request.file_path,
        "line_number": comment_request.line_number,
        "created_at": datetime.now(),
        "resolved": False
    }
    
    comments_db[comment_id] = comment
    
    # Update review comment count
    reviews_db[review_id]["comments_count"] += 1
    reviews_db[review_id]["updated_at"] = datetime.now()
    
    logger.info(f"Added comment {comment_id} to review {review_id}")
    
    return {"comment_id": comment_id, "status": "created"}

@app.get("/reviews/{review_id}/security", response_model=SecurityAnalysisResponse)
async def get_security_analysis(review_id: str):
    """Get security analysis for a review"""
    if review_id not in reviews_db:
        raise HTTPException(status_code=404, detail="Review not found")
    
    # Mock security analysis (integrate with actual security engine)
    security_analysis = {
        "review_id": review_id,
        "security_score": 85,
        "vulnerabilities": [
            {
                "type": "SQL Injection",
                "severity": "High",
                "file": "src/auth/models.py",
                "line": 42,
                "description": "Potential SQL injection vulnerability"
            },
            {
                "type": "XSS",
                "severity": "Medium", 
                "file": "src/views/dashboard.py",
                "line": 128,
                "description": "Unescaped user input in template"
            }
        ],
        "recommendations": [
            "Use parameterized queries for database operations",
            "Implement input validation and sanitization",
            "Add CSRF protection to forms"
        ]
    }
    
    return SecurityAnalysisResponse(**security_analysis)

@app.post("/reviews/{review_id}/approve")
async def approve_review(review_id: str, approver_id: str):
    """Approve a code review"""
    if review_id not in reviews_db:
        raise HTTPException(status_code=404, detail="Review not found")
    
    reviews_db[review_id]["status"] = "approved"
    reviews_db[review_id]["approved_by"] = approver_id
    reviews_db[review_id]["approved_at"] = datetime.now()
    reviews_db[review_id]["updated_at"] = datetime.now()
    
    logger.info(f"Review {review_id} approved by {approver_id}")
    
    return {"status": "approved", "message": "Review approved successfully"}

@app.post("/reviews/{review_id}/reject")
async def reject_review(review_id: str, reviewer_id: str, reason: str):
    """Reject a code review with reason"""
    if review_id not in reviews_db:
        raise HTTPException(status_code=404, detail="Review not found")
    
    reviews_db[review_id]["status"] = "rejected"
    reviews_db[review_id]["rejected_by"] = reviewer_id
    reviews_db[review_id]["rejection_reason"] = reason
    reviews_db[review_id]["rejected_at"] = datetime.now()
    reviews_db[review_id]["updated_at"] = datetime.now()
    
    logger.info(f"Review {review_id} rejected by {reviewer_id}")
    
    return {"status": "rejected", "message": "Review rejected"}

async def process_review(review_id: str):
    """Background task to process a review"""
    logger.info(f"Starting background processing for review {review_id}")
    
    # Simulate review processing
    await asyncio.sleep(2)  # Simulate analysis time
    
    if review_id in reviews_db:
        reviews_db[review_id]["status"] = "in_progress"
        reviews_db[review_id]["files_analyzed"] = 5
        reviews_db[review_id]["security_score"] = 85
        reviews_db[review_id]["updated_at"] = datetime.now()
        
        logger.info(f"Completed processing for review {review_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
