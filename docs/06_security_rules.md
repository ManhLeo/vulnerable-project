# Frontend Architecture
## Purpose
The frontend provides a user interface for:
- uploading source code
- viewing AI analysis results
- visualizing security risks
- managing scan history
---
# Frontend Stack
## Core Technologies
- React
- TypeScript
- Vite
- TailwindCSS
## Additional Libraries
- Axios
- React Router
- Zustand
- React Query
---
# Frontend Goals
- fast user experience
- clean UI structure
- modular components
- scalable architecture
- easy API integration
---
# Main Features
## 1. Source Code Input
Users can:
- paste source code
- upload source files
Supported extensions:
- .c
- .cpp
- .py
- .java
## 2. AI Scan Results
Display:
- vulnerability prediction
- confidence score
- risk level
- suspicious patterns
## 3. Scan History
Users can:
- view previous scans
- review analysis results
- track timestamps
---
# Frontend Architecture
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
FastAPI Backend
---
# Recommended Project Structure
```text
frontend/
├── src/
│   ├── api/
│   ├── components/
│   ├── pages/
│   ├── layouts/
│   ├── store/
│   ├── hooks/
│   ├── types/
│   ├── utils/
│   ├── styles/
│   └── main.tsx
├── public/
├── package.json
└── vite.config.ts
```
---
# Main Pages
## Home Page
Responsibilities:
- upload source code
- trigger AI scan
- display quick results
## Result Page
Responsibilities:
- display prediction details
- show suspicious patterns
- visualize risk level
## History Page
Responsibilities:
- list previous scans
- display scan summaries
---
# State Management
## Recommended Store
Zustand
## Responsibilities
- manage scan results
- manage loading states
- manage API errors
- manage history data
---
# API Integration
## HTTP Client
Axios
## Responsibilities
- send scan requests
- upload source files
- retrieve scan history
- handle API errors
---
# UI Rules
## Required
- responsive layout
- loading indicators
- error handling
- reusable components
- modular styling
## Forbidden
- hardcoded API URLs
- business logic inside components
- duplicated UI components
---
# Security Rules
The frontend must:
- validate file extensions
- limit upload size
- sanitize displayed content
- never expose secrets
---
# Performance Requirements
| Metric | Target |
|---|---|
| Initial Load | < 3 seconds |
| API Response Display | < 1 second |
| Upload Size | 5MB |
---
# Future Features
The frontend architecture must support:
- authentication
- dashboard analytics
- dark mode
- report export
- real-time scanning
- multilingual UI
---
# Final Goal
Build a scalable frontend system capable of:
- interacting with AI analysis APIs
- visualizing vulnerability results
- supporting future product expansion
- providing modern user experience