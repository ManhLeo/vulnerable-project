# Response Rules
## Purpose
This document defines standardized API response rules for the AI-powered source code vulnerability detection system.
All backend APIs must strictly follow these response standards.
---
# Core Rules
## Required
- return JSON responses only
- use consistent response structure
- include status field
- include descriptive messages
- return proper HTTP status codes
## Forbidden
- inconsistent response formats
- raw exception responses
- exposing stack traces
- missing status fields
---
# Standard Success Response
## Format
```json
{
  "status": "success",
  "data": {},
  "message": "Request successful"
}
```
---
# Standard Error Response
## Format
```json
{
  "status": "error",
  "message": "Invalid request",
  "error_code": "BAD_REQUEST"
}
```
---
# Response Rules
## Success Responses
The API must:
- use status=success
- return structured data
- include descriptive messages
## Error Responses
The API must:
- use status=error
- include readable error messages
- include standardized error codes
---
# HTTP Status Codes
| Code | Meaning |
|---|---|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 413 | File Too Large |
| 422 | Validation Error |
| 500 | Internal Server Error |
---
# AI Scan Response
## Example
```json
{
  "status": "success",
  "data": {
    "is_vulnerable": true,
    "confidence": 0.91,
    "risk_level": "HIGH",
    "suspicious_patterns": [
      {
        "pattern": "strcpy",
        "issue": "Potential buffer overflow"
      }
    ]
  },
  "message": "Analysis completed"
}
```
---
# Upload Response
## Example
```json
{
  "status": "success",
  "data": {
    "filename": "example.c",
    "uploaded": true
  },
  "message": "File uploaded successfully"
}
```
---
# Validation Error Response
## Example
```json
{
  "status": "error",
  "message": "Unsupported language",
  "error_code": "INVALID_LANGUAGE"
}
```
---
# Upload Error Response
## Example
```json
{
  "status": "error",
  "message": "Invalid file extension",
  "error_code": "INVALID_FILE_EXTENSION"
}
```
---
# Internal Error Response
## Example
```json
{
  "status": "error",
  "message": "Internal server error",
  "error_code": "INTERNAL_SERVER_ERROR"
}
```
---
# Pagination Response
## Example
```json
{
  "status": "success",
  "data": {
    "items": [],
    "total": 100,
    "page": 1,
    "limit": 10
  },
  "message": "Data retrieved successfully"
}
```
---
# Response Design Rules
## Required
- predictable response format
- frontend-friendly structure
- readable error messages
- reusable response models
## Forbidden
- nested unnecessary fields
- inconsistent naming
- raw backend exceptions
---
# FastAPI Rules
The backend must:
- use Pydantic response schemas
- validate response models
- centralize response formatting
- reuse response utilities
---
# Security Rules
Responses must NEVER expose:
- stack traces
- database details
- filesystem paths
- environment variables
- secrets or tokens
---
# Final Rule
All API responses must prioritize:
- consistency
- readability
- security
- frontend compatibility
- maintainability