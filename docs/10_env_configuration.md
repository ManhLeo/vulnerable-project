# Environment Configuration
## Purpose
This document defines environment variables and configuration rules for the AI-powered source code vulnerability detection system.
---
# Backend Environment Variables
## Core Settings
```env
APP_NAME=AI Vulnerability Detection System
APP_ENV=development
DEBUG=true
API_PREFIX=/api/v1
HOST=0.0.0.0
PORT=8000
```
---
# MongoDB Configuration
```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB=vulnerability_detection
```
---
# AI Model Configuration
```env
MODEL_NAME=codebert
MODEL_PATH=./models/codebert
MODEL_THRESHOLD=0.88
MAX_TOKEN_LENGTH=512
DEVICE=cuda
```
---
# Upload Configuration
```env
MAX_FILE_SIZE=5242880
UPLOAD_DIR=./uploads
ALLOWED_EXTENSIONS=.c,.cpp,.py,.java
```
---
# Security Configuration
```env
SECRET_KEY=change_this_secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
CORS_ORIGINS=http://localhost:5173
```
---
# Logging Configuration
```env
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```
---
# Frontend Environment Variables
## Frontend Settings
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=AI Vulnerability Detection
```
---
# Environment Rules
## Required
- use .env files
- keep secrets outside source code
- separate development and production configs
- validate required environment variables
## Forbidden
- hardcoded secrets
- committing .env files to Git
- exposing private credentials
---
# Backend Configuration Rules
The backend must:
- load environment variables centrally
- validate configuration at startup
- provide fallback defaults when appropriate
- isolate config logic inside core/config.py
---
# Frontend Configuration Rules
The frontend must:
- use Vite environment variables
- avoid hardcoded API URLs
- separate dev and production configs
---
# Recommended Files
```text
backend/
├── .env
├── .env.example
└── app/core/config.py
frontend/
├── .env
├── .env.example
└── vite.config.ts
```
---
# Example .env.example
```env
APP_ENV=development
MONGODB_URL=
SECRET_KEY=
MODEL_PATH=
VITE_API_BASE_URL=
```
---
# Production Rules
## Required
- use secure secrets
- disable debug mode
- restrict CORS origins
- use production database
## Forbidden
- public secrets
- debug logs in production
- unrestricted CORS
---
# Final Goal
Create a secure and scalable environment configuration system capable of:
- supporting development and production
- protecting sensitive credentials
- simplifying deployment configuration
- improving maintainability