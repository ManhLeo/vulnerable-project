# Backend Foundation TODO

- [x] 1) Create backend folder structure (app layers, tests)
- [x] 2) Create core foundation files
  - [x] app/core/config.py
  - [x] app/core/constants.py
  - [x] app/core/logging.py
  - [x] app/core/exceptions.py
  - [x] app/core/response.py
- [x] 3) Create schema models
  - [x] app/schemas/common.py
  - [x] app/schemas/health.py
  - [x] app/schemas/scan.py
  - [x] app/schemas/model.py
- [x] 4) Create DB layer foundation
  - [x] app/db/mongo.py
  - [x] app/db/repositories/scan_repository.py
- [x] 5) Create AI layer foundation
  - [x] app/ai/model_manager.py
  - [x] app/ai/inference.py
- [x] 6) Create analysis layer foundation
  - [x] app/analysis/patterns.py
  - [x] app/analysis/risk.py
- [x] 7) Create service layer
  - [x] app/services/health_service.py
  - [x] app/services/model_service.py
  - [x] app/services/scan_service.py
- [x] 8) Create API layer
  - [x] app/api/routes/health.py
  - [x] app/api/routes/model.py
  - [x] app/api/routes/scan.py
  - [x] app/api/router.py
- [x] 9) Create app entrypoint
  - [x] app/main.py
- [x] 10) Create runtime/devops foundation files
  - [x] requirements.txt
  - [x] .env.example
  - [x] Dockerfile
  - [x] README.md

- [x] 11) Fix verdict consistency
  - [x] Force is_vulnerable=True when findings contain HIGH/CRITICAL
  - [x] Apply severity floor in risk classification
- [x] 12) Re-test impacted endpoints with curl
  - [x] POST /api/v1/scan/code (safe/vuln/edge)
  - [x] POST /api/v1/scan/file (safe/vuln/edge)
  - [x] GET /api/v1/scan/history consistency
- [x] 13) Re-verify affected UI sections
  - [x] Risk Summary
  - [x] Findings Summary
  - [x] Findings panel consistency

# Phase 2 — Integration & Optimization

- [x] 14) Refactor Lifespan
- [x] 15) Stress test AI Model (Locust)
- [ ] 16) Setup Rate Limiting (slowapi / redis)