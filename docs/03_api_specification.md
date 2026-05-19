# API Specification
## Base URL
```text
/api/v1
```
---
# Standard Response Format
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
# Authentication
Current version:
- no authentication required
Future support:
- JWT authentication
- API key authentication
---
# Supported Content Types
- application/json
- multipart/form-data
---
# Endpoints
## 1. Health Check
### GET /health
Description:
- check backend availability
Response:
```json
{
  "status": "healthy"
}
```
---
## 2. Scan Source Code
### POST /scan/code
Description:
- analyze pasted source code using AI
Request Body:
```json
{
  "code": "char buf[10]; strcpy(buf, input);",
  "language": "c"
}
```
### Request Fields
| Field | Type | Required | Description |
|---|---|---|---|
| code | string | Yes | Raw source code |
| language | string | Yes | Programming language |
### Supported Languages
- c
- cpp
- python
- java
### Success Response
```json
{
  "status": "success",
  "data": {
    "is_vulnerable": true,
    "confidence": 0.91,
    "risk_level": "HIGH",
    "suspicious_patterns": [
      {
        "pattern": "strcpy",
        "issue": "Potential buffer overflow"
      }
    ]
  },
  "message": "Analysis completed"
}
```
### Error Response
```json
{
  "status": "error",
  "message": "Unsupported language"
}
```
---
## 3. Scan Source File
### POST /scan/file
Description:
- upload and analyze source code file
Request Type:
```text
multipart/form-data
```
### Request Fields
| Field | Type | Required | Description |
|---|---|---|---|
| file | file | Yes | Source code file |
### Supported Extensions
- .c
- .cpp
- .py
- .java
### Maximum File Size
```text
5MB
```
### Success Response
```json
{
  "status": "success",
  "data": {
    "filename": "example.c",
    "is_vulnerable": true,
    "confidence": 0.91,
    "risk_level": "HIGH",
    "suspicious_patterns": [
      {
        "pattern": "strcpy",
        "issue": "Potential buffer overflow"
      }
    ]
  },
  "message": "File analysis completed"
}
```
### Error Response
```json
{
  "status": "error",
  "message": "Invalid file extension"
}
```
---
## 4. Model Information
### GET /model/info
Description:
- return current AI model information
Response:
```json
{
  "model_name": "CodeBERT",
  "model_version": "1.0",
  "threshold": 0.88
}
```
---
## 5. Scan History
### GET /scan/history
Description:
- retrieve previous scan results
Response:
```json
{
  "status": "success",
  "data": [
    {
      "scan_id": "uuid",
      "language": "c",
      "is_vulnerable": true,
      "confidence": 0.91,
      "created_at": "2026-05-12T12:00:00"
    }
  ]
}
```
---
# Validation Rules
The backend must validate:
- request schema
- file extension
- file size
- supported languages
- empty source code
---
# API Rules
## Required
- async endpoints
- standardized responses
- proper HTTP status codes
- Pydantic validation
- modular routes
## Forbidden
- business logic inside routes
- database access inside routes
- model loading inside endpoints
---
# HTTP Status Codes
| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad Request |
| 404 | Not Found |
| 413 | File Too Large |
| 500 | Internal Server Error |
---
# Future API Extensions
The API architecture must support future:
- authentication
- report export
- batch scanning
- asynchronous scan jobs
- explainability APIs
- CWE classification APIs