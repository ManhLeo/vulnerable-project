# Database Design
## Database System
MongoDB
The database is used to store:
- scan history
- uploaded file metadata
- AI prediction results
- analysis reports
---
# Database Goals
- lightweight structure
- scalable schema
- fast retrieval
- easy future expansion
- flexible document design
---
# Main Collection
## scans
Store vulnerability scan results.
### Document Structure
```json
{
  "scan_id": "uuid",
  "source_type": "code",
  "language": "c",
  "filename": "example.c",
  "code": "char buf[10]; strcpy(buf, input);",
  "prediction": {
    "is_vulnerable": true,
    "confidence": 0.91,
    "risk_level": "HIGH"
  },
  "analysis": {
    "suspicious_patterns": [
      {
        "pattern": "strcpy",
        "issue": "Potential buffer overflow",
        "line": 12
      }
    ]
  },
  "metadata": {
    "model_name": "CodeBERT",
    "model_version": "1.0",
    "threshold": 0.88
  },
  "created_at": "2026-05-12T12:00:00"
}
```
---
# Field Description
| Field | Description |
|---|---|
| scan_id | Unique scan identifier |
| source_type | code or file |
| language | Programming language |
| filename | Uploaded filename |
| code | Raw source code |
| prediction | AI prediction result |
| analysis | Security analysis result |
| metadata | Model information |
| created_at | Scan timestamp |
---
# Prediction Object
```json
{
  "is_vulnerable": true,
  "confidence": 0.91,
  "risk_level": "HIGH"
}
```
---
# Analysis Object
```json
{
  "suspicious_patterns": [
    {
      "pattern": "strcpy",
      "issue": "Potential buffer overflow",
      "line": 12
    }
  ]
}
```
---
# Required Indexes
- scan_id
- created_at
- language
- prediction.is_vulnerable
---
# Future Collections
## users
Store authentication information.
Example:
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "created_at": "2026-05-12T12:00:00"
}
```
## reports
Store exported reports.
Example:
```json
{
  "report_id": "uuid",
  "scan_id": "uuid",
  "report_type": "pdf",
  "created_at": "2026-05-12T12:00:00"
}
```
## model_logs
Store inference logs.
Example:
```json
{
  "log_id": "uuid",
  "model_name": "CodeBERT",
  "inference_time": 0.82,
  "created_at": "2026-05-12T12:00:00"
}
```
---
# Database Rules
## Required
- use UUID identifiers
- store timestamps in ISO format
- keep schema flexible
- support future extensions
## Forbidden
- storing executable files
- storing unnecessary binary data
- storing sensitive credentials
---
# Security Rules
The database must:
- sanitize stored data
- validate input before insert
- prevent injection attacks
- never store raw secrets
---
# Scalability Requirements
The database design must support future:
- CWE classification
- explainability
- line-level localization
- multi-model predictions
- report generation
---
# Backend Integration
The backend should access MongoDB through:
- repository layer
- centralized database service
Routes must NEVER directly access the database.
---
# Repository Structure
```text
app/
├── db/
│   ├── mongodb.py
│   └── repositories/
│       ├── scan_repository.py
│       ├── report_repository.py
│       └── user_repository.py
```
---
# Final Goal
Build a scalable database layer capable of:
- storing AI scan results
- supporting analytics
- enabling future security research
- supporting production deployment