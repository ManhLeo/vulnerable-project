# Error Handling
## Purpose
This document defines standardized error handling rules for the AI-powered source code vulnerability detection system.
---
# Error Handling Goals
- provide consistent API responses
- improve debugging
- prevent internal exposure
- simplify frontend integration
- improve system stability
---
# Standard Error Response
## Format
```json
{
  "status": "error",
  "message": "Invalid request",
  "error_code": "BAD_REQUEST"
}
```
---
# Error Categories
## Validation Errors
Examples:
- invalid request body
- unsupported language
- empty source code
- invalid file extension
## Upload Errors
Examples:
- file too large
- corrupted file
- unsupported file type
## AI Inference Errors
Examples:
- tokenizer failure
- model loading failure
- inference timeout
- invalid prediction output
## Database Errors
Examples:
- MongoDB connection failure
- insert failure
- query timeout
## Internal Server Errors
Examples:
- unexpected exceptions
- service failures
- configuration errors
---
# HTTP Status Codes
| Code | Meaning |
|---|---|
| 200 | Success |
| 400 | Bad Request |
| 401 | Unauthorized |
| 404 | Not Found |
| 413 | File Too Large |
| 422 | Validation Error |
| 500 | Internal Server Error |
---
# FastAPI Exception Handling
## Required
- centralized exception handlers
- custom error responses
- async-safe exception handling
- request validation handling
## Forbidden
- exposing stack traces
- returning raw exceptions
- inconsistent error formats
---
# Validation Error Example
```json
{
  "status": "error",
  "message": "Unsupported language",
  "error_code": "INVALID_LANGUAGE"
}
```
---
# Upload Error Example
```json
{
  "status": "error",
  "message": "File size exceeds limit",
  "error_code": "FILE_TOO_LARGE"
}
```
---
# AI Error Example
```json
{
  "status": "error",
  "message": "Inference failed",
  "error_code": "MODEL_INFERENCE_ERROR"
}
```
---
# Logging Rules
The backend must log:
- request errors
- validation failures
- inference failures
- database failures
- unexpected exceptions
---
# Security Rules
The system must NEVER:
- expose stack traces
- expose database details
- expose internal paths
- expose secrets or tokens
---
# Frontend Error Handling
The frontend must:
- display user-friendly messages
- handle loading failures
- handle timeout errors
- handle upload failures
---
# Recommended Backend Structure
```text
backend/
├── app/
│   ├── core/
│   │   ├── exceptions.py
│   │   ├── handlers.py
│   │   └── logging.py
```
---
# Error Handling Flow
Request
↓
Validation
↓
Service Execution
↓
Exception Handler
↓
Standardized JSON Response
---
# Final Goal
Build a reliable error handling system capable of:
- improving API consistency
- simplifying debugging
- protecting backend internals
- supporting production deployment