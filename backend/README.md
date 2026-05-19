# Vulnerability Detection Backend (Foundation)

Production-oriented FastAPI backend foundation following clean architecture layers:

- API Layer
- Service Layer
- AI Inference Layer
- Analysis Layer
- Database Layer

## Run locally

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## API Prefix

`/api/v1`

## Foundation Endpoints

- `GET /api/v1/health`
- `POST /api/v1/scan/code`
- `POST /api/v1/scan/file`
- `GET /api/v1/scan/history`
- `GET /api/v1/model/info`

## Response Contract

Success:
```json
{
  "status": "success",
  "data": {},
  "message": "..."
}
```

Error:
```json
{
  "status": "error",
  "message": "...",
  "error_code": "..."
}
