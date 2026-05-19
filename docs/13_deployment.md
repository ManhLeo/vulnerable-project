# Deployment Guide
## Purpose
This document defines deployment requirements and production setup for the AI-powered source code vulnerability detection system.
---
# Deployment Goals
- support production environments
- ensure scalability
- simplify deployment
- improve reliability
- secure backend services
---
# Deployment Stack
## Backend
- FastAPI
- Uvicorn
- Docker
## Frontend
- React
- Vite
- Nginx
## Database
- MongoDB
---
# Deployment Architecture
Frontend
↓
Nginx
↓
FastAPI Backend
↓
AI Inference Layer
↓
MongoDB
---
# Backend Deployment
## Required Tasks
- build Docker image
- configure environment variables
- expose API port
- enable logging
- configure production settings
## Backend Start Command
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
---
# Frontend Deployment
## Required Tasks
- build production assets
- configure API endpoint
- serve static files using Nginx
## Frontend Build Command
```bash
npm run build
```
---
# Docker Requirements
## Backend Dockerfile
Required:
- Python 3.11+
- dependency installation
- environment configuration
- production startup command
## Frontend Dockerfile
Required:
- Node.js build stage
- Nginx production stage
- static asset serving
---
# Docker Compose Structure
```text
docker-compose.yml
services:
  - backend
  - frontend
  - mongodb
```
---
# Environment Variables
## Backend
```env
APP_ENV=production
DEBUG=false
MONGODB_URL=mongodb://mongodb:27017
MODEL_PATH=./models/codebert
```
## Frontend
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```
---
# Security Rules
The production system must:
- disable debug mode
- secure environment variables
- restrict CORS origins
- validate uploaded files
- never expose secrets
---
# Performance Rules
## Backend
- async endpoints required
- singleton AI model required
- optimized inference required
## Frontend
- optimized production build
- minimized assets
- caching enabled
---
# Monitoring Requirements
The production system must:
- enable logging
- monitor API health
- monitor inference latency
- monitor backend failures
---
# Recommended Ports
| Service | Port |
|---|---|
| Frontend | 80 |
| Backend | 8000 |
| MongoDB | 27017 |
---
# Recommended Deployment Structure
```text
server/
├── backend/
├── frontend/
├── docker/
├── models/
├── logs/
└── docker-compose.yml
```
---
# Production Rules
## Required
- use Docker containers
- isolate backend services
- enable restart policies
- use production configs
## Forbidden
- debug mode in production
- hardcoded secrets
- unrestricted uploads
---
# Future Deployment Support
The deployment architecture must support:
- cloud deployment
- load balancing
- scalable inference
- CI/CD pipelines
- container orchestration
---
# Final Goal
Build a scalable production deployment capable of:
- serving AI inference APIs
- supporting frontend applications
- handling production traffic
- maintaining system reliability