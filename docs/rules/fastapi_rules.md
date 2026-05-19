# FastAPI Rules
## Purpose
This document defines mandatory FastAPI backend development standards for the AI-powered source code vulnerability detection system.
All backend APIs and services must strictly follow these rules.
---
# Core Rules
## Required
- use FastAPI
- use async endpoints
- use APIRouter
- validate requests using Pydantic
- return standardized JSON responses
- follow clean architecture
## Forbidden
- business logic inside routes
- direct DB access inside endpoints
- loading AI models per request
- duplicated API logic
- exposing internal exceptions
---
# Backend Structure
```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   └── deps/
│   ├── services/
│   ├── ai/
│   ├── analysis/
│   ├── db/
│   ├── schemas/
│   ├── core/
│   └── main.py
```
---
# API Layer Rules
The API layer must:
- receive requests
- validate request data
- call service layer functions
- return standardized responses
The API layer must NEVER:
- perform AI inference directly
- access MongoDB directly
- contain business workflows
---
# Route Rules
## Required
- modular route files
- versioned API prefixes
- reusable route structure
- proper HTTP status codes
## Forbidden
- oversized route files
- duplicated route handlers
- inline business logic
---
# Pydantic Rules
The backend must:
- validate all requests
- validate all responses
- use typed schemas
- separate request and response models
---
# Dependency Injection Rules
The backend must:
- use FastAPI Depends()
- centralize dependencies
- inject repositories and services properly
---
# Async Rules
## Required
- async endpoints
- async database operations
- async-safe services
## Forbidden
- blocking operations inside async routes
- synchronous DB access
---
# Response Rules
## Success Response
```json
{
  "status": "success",
  "data": {},
  "message": "Request successful"
}
```
## Error Response
```json
{
  "status": "error",
  "message": "Invalid request",
  "error_code": "BAD_REQUEST"
}
```
---
# Error Handling Rules
The backend must:
- use centralized exception handlers
- log backend failures
- prevent stack trace exposure
- return consistent error responses
---
# Security Rules
The backend must:
- validate uploaded files
- sanitize user inputs
- reject unsupported extensions
- prevent path traversal
- never execute uploaded code
---
# AI Integration Rules
The FastAPI layer must:
- call AI services only
- never load models in routes
- never retrain during runtime
- isolate inference logic
---
# Database Rules
The backend must:
- use repository pattern
- isolate DB operations
- use reusable repositories
- avoid raw queries in routes
---
# Logging Rules
The backend must log:
- API requests
- response times
- backend exceptions
- inference duration
- upload failures
---
# Performance Rules
## Required Targets
- API response < 2 seconds
- inference < 1 second
- optimized async operations
---
# Deployment Rules
The backend must support:
- Docker deployment
- environment-based configs
- production startup configuration
---
# Coding Standards
## Required
- type hints
- modular services
- reusable utilities
- readable naming conventions
## Forbidden
- magic values
- duplicated validation logic
- mixed responsibilities
---
# Final Rule
All FastAPI backend code must prioritize:
- scalability
- maintainability
- security
- performance
- clean architecture