# AI Development Rules
## Purpose
This document defines mandatory rules for AI-assisted development.
All generated code must follow these standards.
---
# General Rules
## Required
- write clean and modular code
- use meaningful naming conventions
- keep functions small and reusable
- separate business logic from routes
- follow project architecture strictly
- use async programming where necessary
## Forbidden
- duplicated logic
- hardcoded credentials
- direct database access in routes
- loading AI model per request
- oversized components or files
---
# Backend Rules
## FastAPI Rules
- use APIRouter
- use dependency injection
- validate requests with Pydantic
- return standardized JSON responses
- use async endpoints
## Service Layer Rules
- keep business logic inside services
- avoid logic inside controllers
- use reusable service methods
## Database Rules
- use repository pattern
- isolate database operations
- validate data before insert
- use UUID identifiers
## AI Rules
- load model once at startup
- keep inference separate from API routes
- never retrain during runtime
- never execute uploaded source code
---
# Frontend Rules
## React Rules
- use functional components
- use TypeScript interfaces
- separate UI and logic
- create reusable components
## State Management Rules
- use Zustand for global state
- avoid unnecessary prop drilling
- isolate API state handling
## UI Rules
- responsive layout required
- loading states required
- error states required
- avoid duplicated UI logic
---
# File Structure Rules
## Backend Structure
```text
backend/
├── app/
├── tests/
├── requirements.txt
└── Dockerfile
```
## Frontend Structure
```text
frontend/
├── src/
├── public/
├── package.json
└── vite.config.ts
```
---
# API Rules
## Required
- versioned APIs
- modular routes
- standardized responses
- proper status codes
## Forbidden
- inconsistent response formats
- direct exception exposure
- business logic in endpoints
---
# Security Rules
The system must:
- validate uploaded files
- sanitize user input
- limit upload size
- reject unsupported extensions
- prevent path traversal
- never expose secrets
---
# Performance Rules
## Backend
- API response < 2 seconds
- inference < 1 second
## Frontend
- initial load < 3 seconds
- optimized rendering required
---
# Logging Rules
The backend must log:
- API requests
- inference results
- errors
- performance metrics
---
# Code Quality Rules
## Required
- type hints
- linting
- formatted code
- modular architecture
- reusable utilities
## Recommended Tools
- black
- ruff
- eslint
- prettier
---
# Testing Rules
## Backend Testing
- test API endpoints
- test services
- test inference pipeline
## Frontend Testing
- test components
- test API integration
- test user flows
---
# Git Rules
## Branch Naming
```text
feature/feature-name
bugfix/bug-name
hotfix/hotfix-name
```
## Commit Style
```text
feat: add scan API
fix: resolve upload validation bug
refactor: improve inference service
```
---
# Final Rule
All generated code must prioritize:
- scalability
- maintainability
- security
- performance
- clean architecture