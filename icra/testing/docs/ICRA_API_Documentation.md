# ICRA API Documentation

## Overview

The Interactive Code Review Agent (ICRA) provides a comprehensive REST API for managing code reviews, security analysis, and collaboration features.

## Base URL

```
http://localhost:8000
```

## Authentication

Currently, the API does not require authentication for development purposes. In production, implement proper authentication mechanisms.

## Endpoints

### Health Check

#### GET /
Returns basic API information and health status.

**Response:**
```json
{
  "message": "ICRA API is running",
  "version": "1.0.0",
  "status": "healthy",
  "timestamp": "2025-09-06T21:30:00.000Z"
}
```

#### GET /health
Detailed health check including service status.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-06T21:30:00.000Z",
  "services": {
    "api": "running",
    "database": "connected",
    "security_engine": "active"
  }
}
```

### Reviews

#### POST /reviews
Create a new code review.

**Request Body:**
```json
{
  "repository_url": "https://github.com/user/repo",
  "pull_request_id": "123",
  "reviewer_id": "reviewer_username",
  "priority": "high"
}
```

**Response:**
```json
{
  "review_id": "uuid-string",
  "status": "pending",
  "created_at": "2025-09-06T21:30:00.000Z"
}
```

#### GET /reviews
List all reviews with optional filtering.

**Query Parameters:**
- `status` (optional): Filter by review status
- `limit` (optional): Maximum number of results (default: 10)

**Response:**
```json
{
  "reviews": [
    {
      "id": "review-id",
      "repository_url": "https://github.com/user/repo",
      "pull_request_id": "123",
      "status": "in_progress",
      "created_at": "2025-09-06T21:30:00.000Z",
      "security_score": 85
    }
  ],
  "total": 1,
  "filtered": 1
}
```

#### GET /reviews/{review_id}
Get detailed information about a specific review.

**Response:**
```json
{
  "review": {
    "id": "review-id",
    "repository_url": "https://github.com/user/repo",
    "pull_request_id": "123",
    "status": "in_progress",
    "created_at": "2025-09-06T21:30:00.000Z",
    "security_score": 85,
    "files_analyzed": 5,
    "comments_count": 3
  },
  "comments": [
    {
      "id": "comment-id",
      "user_id": "user123",
      "text": "This looks good\!",
      "file_path": "src/main.py",
      "line_number": 42,
      "created_at": "2025-09-06T21:30:00.000Z"
    }
  ],
  "comment_count": 1
}
```

### Comments

#### POST /reviews/{review_id}/comments
Add a comment to a review.

**Request Body:**
```json
{
  "review_id": "review-id",
  "user_id": "user123",
  "text": "Consider adding error handling here",
  "file_path": "src/main.py",
  "line_number": 42
}
```

**Response:**
```json
{
  "comment_id": "comment-uuid",
  "status": "created"
}
```

### Security Analysis

#### GET /reviews/{review_id}/security
Get security analysis results for a review.

**Response:**
```json
{
  "review_id": "review-id",
  "security_score": 85,
  "vulnerabilities": [
    {
      "type": "SQL Injection",
      "severity": "High",
      "file": "src/auth/models.py",
      "line": 42,
      "description": "Potential SQL injection vulnerability"
    }
  ],
  "recommendations": [
    "Use parameterized queries for database operations",
    "Implement input validation and sanitization"
  ]
}
```

### Review Actions

#### POST /reviews/{review_id}/approve
Approve a code review.

**Query Parameters:**
- `approver_id`: ID of the user approving the review

**Response:**
```json
{
  "status": "approved",
  "message": "Review approved successfully"
}
```

#### POST /reviews/{review_id}/reject
Reject a code review.

**Query Parameters:**
- `reviewer_id`: ID of the user rejecting the review
- `reason`: Reason for rejection

**Response:**
```json
{
  "status": "rejected",
  "message": "Review rejected"
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 404 Not Found
```json
{
  "detail": "Review not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "repository_url"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. In production, implement appropriate rate limiting based on your requirements.

## WebSocket Support

Real-time collaboration features will be implemented using WebSocket connections for:
- Live comments and discussions
- User presence indicators
- Real-time review status updates

## SDK Examples

### Python
```python
import requests

# Create a review
response = requests.post("http://localhost:8000/reviews", json={
    "repository_url": "https://github.com/user/repo",
    "pull_request_id": "123",
    "reviewer_id": "reviewer123"
})

review_data = response.json()
review_id = review_data["review_id"]

# Add a comment
requests.post(f"http://localhost:8000/reviews/{review_id}/comments", json={
    "review_id": review_id,
    "user_id": "user123",
    "text": "Great work\!",
    "file_path": "src/main.py",
    "line_number": 10
})

# Get security analysis
security_response = requests.get(f"http://localhost:8000/reviews/{review_id}/security")
security_data = security_response.json()
```

### JavaScript
```javascript
// Create a review
const response = await fetch('http://localhost:8000/reviews', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    repository_url: 'https://github.com/user/repo',
    pull_request_id: '123',
    reviewer_id: 'reviewer123'
  })
});

const reviewData = await response.json();
const reviewId = reviewData.review_id;

// Add a comment
await fetch(`http://localhost:8000/reviews/${reviewId}/comments`, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    review_id: reviewId,
    user_id: 'user123',
    text: 'Great work\!',
    file_path: 'src/main.py',
    line_number: 10
  })
});
```

## OpenAPI Documentation

The API provides interactive documentation at:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
