# System Overview
## Project Name
AI-Powered Source Code Vulnerability Detection System
---
# Project Description
This project is a web-based AI system for analyzing source code vulnerabilities using deep learning and static analysis techniques.
The system allows users to:
- upload source code files
- paste raw source code
- run AI vulnerability analysis
- detect suspicious security patterns
- receive structured analysis results
The backend is developed using FastAPI and integrates a CodeBERT-based AI model.
---
# Main Objectives
## Functional Objectives
- analyze source code vulnerabilities
- support file upload and raw code input
- return AI prediction results
- detect suspicious coding patterns
- store scan history
## Technical Objectives
- build scalable backend architecture
- use modular and maintainable structure
- support future AI model expansion
- provide production-ready APIs
---
# Core Features
## 1. Source Code Upload
Users can:
- paste source code directly
- upload source code files
Supported file types:
- .c
- .cpp
- .py
- .java
## 2. AI Vulnerability Detection
The AI model performs binary classification:
- vulnerable
- non-vulnerable
Example output:
```json
{
  "is_vulnerable": true,
  "confidence": 0.91
}
```
## 3. Security Pattern Analysis
The backend performs additional rule-based analysis to detect suspicious patterns.
Examples:
- strcpy
- gets
- eval
- system()
- unsafe SQL concatenation
Example output:
```json
{
  "pattern": "strcpy",
  "issue": "Potential buffer overflow"
}
```
## 4. Risk Assessment
Prediction confidence is mapped into risk levels.
| Confidence | Risk |
|---|---|
| > 0.90 | HIGH |
| 0.70 - 0.90 | MEDIUM |
| < 0.70 | LOW |
## 5. Scan History
The system stores:
- prediction results
- uploaded file metadata
- timestamps
- scan summaries
---
# AI Model
## Current Model
CodeBERT
## AI Frameworks
- PyTorch
- HuggingFace Transformers
## AI Task
Binary classification only:
- vulnerable
- non-vulnerable
The AI model does NOT directly predict:
- CWE type
- vulnerable line
- severity explanation
Those features belong to:
- analysis layer
- rule engine
- explainability system
---
# System Architecture
Frontend
↓
FastAPI Backend
↓
API Layer
↓
Service Layer
↓
AI Inference Layer
↓
Analysis Layer
↓
MongoDB
---
# Backend Responsibilities
The backend handles:
- request validation
- file upload processing
- AI inference
- suspicious pattern analysis
- risk scoring
- scan history storage
- standardized API responses
---
# Frontend Responsibilities
The frontend handles:
- source code upload
- displaying scan results
- risk visualization
- scan history visualization
---
# Technology Stack
## Backend
- FastAPI
- Python 3.11+
- Pydantic
- Uvicorn
## AI
- PyTorch
- Transformers
- CodeBERT
## Database
- MongoDB
## Frontend
- React
- TypeScript
## Deployment
- Docker
- Nginx
---
# Design Principles
## Clean Architecture
Separate:
- API layer
- service layer
- AI layer
- analysis layer
- database layer
## Scalability
The system must support future:
- CWE classification
- explainability
- localization
- multiple AI models
## Security
The backend must:
- validate uploaded files
- sanitize inputs
- reject dangerous extensions
- never execute uploaded code
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
# Expected Workflow
User Uploads Code
↓
Backend Validation
↓
Preprocessing
↓
AI Inference
↓
Security Pattern Analysis
↓
Risk Assessment
↓
JSON Response
↓
Frontend Visualization
---
# Important Constraints
The backend must NEVER:
- execute uploaded code
- retrain models during runtime
- expose stack traces
- expose model internals
The backend must ALWAYS:
- validate inputs
- return structured JSON
- isolate business logic from routes
---
# Final Goal
Build a lightweight AI-powered security analysis platform capable of:
- analyzing source code
- detecting vulnerabilities
- providing security insights
- supporting future AI security research and deployment