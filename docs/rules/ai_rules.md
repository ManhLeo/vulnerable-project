# AI Rules
## Purpose
This document defines mandatory AI-generated coding rules for the AI-powered source code vulnerability detection system.
All generated code must strictly follow these standards.
---
# General Rules
## Required
- write clean and maintainable code
- follow modular architecture
- separate concerns properly
- use meaningful naming conventions
- keep files organized
- create reusable components and services
## Forbidden
- duplicated logic
- oversized files
- hardcoded credentials
- mixed responsibilities
- exposing internal system details
---
# Backend Rules
## FastAPI Rules
- use APIRouter
- use async endpoints
- validate requests using Pydantic
- use dependency injection
- return standardized JSON responses
## Architecture Rules
- separate routes and business logic
- use service layer architecture
- use repository pattern
- isolate AI inference logic
## Database Rules
- use MongoDB repositories
- isolate DB operations
- validate stored data
- use UUID identifiers
## AI Rules
- load model once at startup
- use singleton inference model
- preprocess source code safely
- never retrain during runtime
- never execute uploaded code
---
# Frontend Rules
## React Rules
- use React with TypeScript
- use functional components
- separate UI and API logic
- create reusable components
## State Management Rules
- use Zustand
- manage loading states globally
- manage API errors consistently
## Styling Rules
- use TailwindCSS
- keep UI responsive
- avoid duplicated styling
---
# API Rules
## Required
- versioned APIs
- centralized error handling
- proper HTTP status codes
- request validation
- standardized responses
## Forbidden
- inconsistent response structures
- business logic inside endpoints
- exposing raw exceptions
---
# Security Rules
The system must:
- validate uploaded files
- sanitize all user inputs
- reject unsupported extensions
- prevent path traversal
- never expose secrets
- never execute uploaded source code
---
# Performance Rules
## Backend Targets
- API response < 2 seconds
- inference < 1 second
- async-safe operations
## Frontend Targets
- initial load < 3 seconds
- optimized rendering
- minimal rerenders
---
# Logging Rules
The backend must log:
- API requests
- inference duration
- upload failures
- database failures
- backend exceptions
---
# File Structure Rules
## Backend
```text
backend/
├── app/
├── tests/
├── requirements.txt
└── Dockerfile
```
## Frontend
```text
frontend/
├── src/
├── public/
├── package.json
└── vite.config.ts
```
---
# Coding Standards
## Required
- type hints
- TypeScript interfaces
- reusable utilities
- centralized configs
- readable naming conventions
## Forbidden
- magic values
- duplicated validation logic
- oversized components
---
# Deployment Rules
The system must support:
- Docker deployment
- environment variables
- production configuration
- scalable architecture
---
# Testing Rules
## Backend
- test APIs
- test inference pipeline
- test upload validation
## Frontend
- test components
- test API integration
- test user flows
---
# Final Rule
All generated code must prioritize:
- scalability
- maintainability
- security
- performance
- clean architecture