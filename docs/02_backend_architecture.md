# Backend Architecture
## Architecture Style
The backend follows Clean Architecture principles to ensure:
- scalability
- maintainability
- modularity
- separation of concerns
- reusable components
---
# Architecture Goals
- build production-ready backend APIs
- isolate AI inference logic
- support future feature expansion
- improve maintainability
- optimize inference performance
---
# High-Level Architecture
Client
↓
FastAPI API Layer
↓
Service Layer
↓
AI Inference Layer
↓
Analysis Layer
↓
Database Layer
↓
MongoDB
---
# Layer Structure
## 1. API Layer
### Responsibilities
- receive HTTP requests
- validate request data
- return standardized responses
- handle HTTP status codes
### Rules
- no business logic
- no AI logic
- no database access
- routes must remain lightweight
### Technologies
- FastAPI
- Pydantic
---
## 2. Service Layer
### Responsibilities
- handle business logic
- coordinate workflows
- communicate between layers
- manage scan processes
### Example Services
- scan_service
- analysis_service
- storage_service
### Rules
- reusable service functions
- centralized logic
- async support
---
## 3. AI Inference Layer
### Responsibilities
- load AI model
- preprocess source code
- tokenize input
- run inference
- return prediction results
### Components
- model_loader.py
- preprocessing.py
- inference.py
- tokenizer.py
### Rules
- model loads once at startup
- singleton model instance
- inference only
- no training during runtime
---
## 4. Analysis Layer
### Responsibilities
- detect suspicious patterns
- perform heuristic analysis
- generate issue explanations
- calculate risk levels
### Example Detections
- strcpy
- gets
- eval
- system()
- SQL injection patterns
### Rules
- analysis logic separated from AI model
- reusable detection modules
- modular rule engine
---
## 5. Database Layer
### Responsibilities
- store scan history
- store metadata
- retrieve reports
- manage persistence
### Rules
- repository pattern
- centralized database access
- no direct DB access from routes
---
# Request Workflow
User Request
↓
API Route
↓
Request Validation
↓
Service Layer
↓
AI Inference
↓
Pattern Analysis
↓
Risk Assessment
↓
Database Storage
↓
JSON Response
---
# Project Structure
```text
backend/
├── app/
│   ├── api/
│   ├── core/
│   ├── services/
│   ├── ai/
│   ├── analysis/
│   ├── db/
│   ├── schemas/
│   └── main.py
├── tests/
├── requirements.txt
└── Dockerfile
```
---
# Dependency Injection
FastAPI Depends() must be used for:
- database services
- repositories
- configuration
- reusable services
---
# Standard API Response
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
  "message": "Invalid request"
}
```
---
# Performance Requirements
| Metric | Target |
|---|---|
| API Response Time | < 2 seconds |
| AI Inference Time | < 1 second |
| Upload Size | 5MB |
---
# Security Requirements
The backend must:
- validate uploaded files
- sanitize inputs
- reject dangerous extensions
- limit upload size
- prevent path traversal
- never execute uploaded code
---
# Scalability Requirements
The architecture must support future:
- CWE classification
- explainability
- line-level localization
- multiple AI models
- async task queues
- distributed inference
---
# Logging Requirements
The backend must support:
- request logging
- inference logging
- error logging
- performance monitoring
---
# Important Rules
## Forbidden
- business logic inside routes
- loading model per request
- direct database access in routes
- duplicated analysis logic
## Required
- service layer
- modular architecture
- singleton AI model
- centralized configuration
- reusable components
- async endpoints
---
# Final Architecture Goal
Build a scalable and maintainable backend system capable of:
- handling AI inference efficiently
- analyzing source code vulnerabilities
- supporting future security research
- scaling into production environments