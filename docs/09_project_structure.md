# Project Structure
## Purpose
This document defines the complete project structure for the AI-powered source code vulnerability detection system.
---
# Root Structure
```text
project-root/
├── backend/
├── frontend/
├── docs/
├── scripts/
├── models/
├── datasets/
├── docker/
├── .env
├── .gitignore
├── README.md
└── docker-compose.yml
```
---
# Backend Structure
```text
backend/
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py
│   │   │   ├── scan.py
│   │   │   ├── upload.py
│   │   │   └── history.py
│   │   └── deps/
│   ├── services/
│   │   ├── scan_service.py
│   │   ├── analysis_service.py
│   │   └── storage_service.py
│   ├── ai/
│   │   ├── model_loader.py
│   │   ├── inference.py
│   │   ├── tokenizer.py
│   │   └── preprocessing.py
│   ├── analysis/
│   │   ├── regex_engine.py
│   │   ├── pattern_detector.py
│   │   └── risk_engine.py
│   ├── db/
│   │   ├── mongodb.py
│   │   └── repositories/
│   │       ├── scan_repository.py
│   │       ├── report_repository.py
│   │       └── user_repository.py
│   ├── schemas/
│   │   ├── request.py
│   │   ├── response.py
│   │   └── scan.py
│   ├── core/
│   │   ├── config.py
│   │   ├── logging.py
│   │   └── security.py
│   └── main.py
├── tests/
├── requirements.txt
└── Dockerfile
```
---
# Frontend Structure
```text
frontend/
├── src/
│   ├── api/
│   │   └── client.ts
│   ├── components/
│   │   ├── UploadBox.tsx
│   │   ├── ResultCard.tsx
│   │   └── RiskBadge.tsx
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   ├── ResultPage.tsx
│   │   └── HistoryPage.tsx
│   ├── layouts/
│   │   └── MainLayout.tsx
│   ├── store/
│   │   └── scanStore.ts
│   ├── hooks/
│   ├── types/
│   ├── utils/
│   ├── styles/
│   ├── App.tsx
│   └── main.tsx
├── public/
├── package.json
└── vite.config.ts
```
---
# Documentation Structure
```text
docs/
├── 01_system_overview.md
├── 02_backend_architecture.md
├── 03_api_specification.md
├── 04_ai_inference_pipeline.md
├── 05_database_design.md
├── 06_frontend_architecture.md
├── 07_ai_development_rules.md
├── 08_backend_development_tasks.md
└── 09_project_structure.md
```
---
# Models Structure
```text
models/
├── codebert/
│   ├── config.json
│   ├── tokenizer/
│   └── weights/
```
---
# Dataset Structure
```text
datasets/
├── raw/
├── processed/
└── splits/
```
---
# Docker Structure
```text
docker/
├── backend/
├── frontend/
└── nginx/
```
---
# Structure Rules
## Required
- modular architecture
- separated backend/frontend
- reusable services
- isolated AI logic
- centralized configuration
## Forbidden
- duplicated business logic
- mixed frontend/backend files
- direct model access in routes
- oversized components
---
# Final Goal
Maintain a scalable and clean project structure capable of:
- supporting AI inference systems
- scaling into production
- enabling future feature expansion
- improving maintainability