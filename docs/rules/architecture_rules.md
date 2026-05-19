# Architecture Rules
## Purpose
This document defines mandatory architecture standards for the AI-powered source code vulnerability detection system.
All backend and frontend development must strictly follow these architecture rules.
---
# Core Principles
The system architecture must prioritize:
- scalability
- maintainability
- modularity
- separation of concerns
- production readiness
---
# Clean Architecture Rules
## Required
- separate presentation and business logic
- isolate AI inference logic
- isolate database operations
- centralize configuration
- create reusable services
## Forbidden
- business logic inside routes
- direct database access in controllers
- mixed responsibilities
- tightly coupled modules
---
# Backend Architecture
## Required Layers
Client
↓
API Layer
↓
Service Layer
↓
AI Inference Layer
↓
Analysis Layer
↓
Database Layer
---
# API Layer Rules
The API layer must:
- receive HTTP requests
- validate requests
- return standardized responses
- handle HTTP status codes
The API layer must NEVER:
- contain business logic
- access MongoDB directly
- perform AI inference directly
---
# Service Layer Rules
The service layer must:
- handle business workflows
- coordinate backend operations
- communicate with repositories
- call AI inference services
The service layer must NEVER:
- return raw database objects
- contain frontend logic
---
# AI Layer Rules
The AI layer must:
- load CodeBERT once at startup
- preprocess source code safely
- tokenize inputs
- perform inference only
The AI layer must NEVER:
- retrain models during runtime
- execute uploaded source code
---
# Analysis Layer Rules
The analysis layer must:
- detect suspicious patterns
- perform regex analysis
- generate heuristic results
- calculate risk levels
The analysis layer must remain independent from:
- API routes
- frontend logic
---
# Database Layer Rules
The database layer must:
- use repository pattern
- isolate MongoDB access
- centralize database operations
- validate stored data
The database layer must NEVER:
- expose raw DB access to routes
- mix AI inference logic
---
# Frontend Architecture
## Required Layers
User Interface
↓
Pages
↓
Components
↓
State Management
↓
API Services
↓
Backend APIs
---
# Frontend Rules
The frontend must:
- separate UI and API logic
- use reusable components
- centralize API requests
- manage global state cleanly
The frontend must NEVER:
- hardcode API URLs
- duplicate layouts
- place API logic directly inside UI rendering
---
# Project Structure Rules
## Required
```text
project-root/
├── backend/
├── frontend/
├── docs/
├── models/
├── datasets/
└── docker/
```
## Forbidden
- mixed backend/frontend files
- duplicated modules
- oversized directories
---
# Configuration Rules
The system must:
- use environment variables
- centralize configs
- separate development and production configs
The system must NEVER:
- hardcode secrets
- expose environment credentials
---
# Scalability Rules
The architecture must support future:
- CWE classification
- explainability
- authentication
- multi-model inference
- report export
- dashboard analytics
---
# Security Rules
The architecture must:
- validate uploads
- sanitize inputs
- prevent path traversal
- protect internal services
- isolate inference execution
---
# Performance Rules
## Backend
- async-safe architecture required
- singleton AI model required
- optimized inference pipeline required
## Frontend
- optimized rendering required
- efficient state updates required
---
# Final Rule
All development must strictly follow:
- clean architecture
- modular structure
- service isolation
- reusable components
- production-ready standards