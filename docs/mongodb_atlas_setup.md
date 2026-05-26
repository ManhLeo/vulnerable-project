# MongoDB Atlas Setup

## 1. Create Atlas cluster

1. Sign in to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas).
2. Create a free/shared cluster.
3. Choose a cloud region close to your backend deployment.

## 2. Database user

1. **Database Access** → **Add New Database User**.
2. Use password authentication.
3. Grant `readWrite` on the application database (for example `vuln_scanner`).

## 3. Network access

1. **Network Access** → **Add IP Address**.
2. For local development, add your current IP or `0.0.0.0/0` (development only).
3. For production, restrict to backend server IPs.

## 4. Connection string

1. **Database** → **Connect** → **Drivers**.
2. Copy the URI, for example:

```text
mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
```

3. Set backend environment variables in `backend/.env`:

```env
MONGODB_URL=mongodb+srv://<username>:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
MONGODB_DB_NAME=vuln_scanner
USE_IN_MEMORY_REPOSITORY=false
```

## 5. Create indexes

From `backend/`:

```bash
python scripts/mongodb_create_indexes.py
```

Indexes created on collection `scans`:

| Index | Fields | Purpose |
|-------|--------|---------|
| `idx_scan_id` | `scan_id` (unique) | Fast lookup by business id |
| `idx_created_at` | `created_at` desc | History sorting |
| `idx_language` | `language` | Language filter |
| `idx_prediction_is_vulnerable` | `prediction.is_vulnerable` | Vulnerable filter |
| `idx_prediction_risk_level` | `prediction.risk_level` | Risk filter |

Indexes are also ensured automatically on FastAPI startup.

## 6. Verify

```bash
cd backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Test:

```bash
curl http://127.0.0.1:8000/api/v1/health
curl "http://127.0.0.1:8000/api/v1/scan/history?page=1&limit=5"
curl http://127.0.0.1:8000/api/v1/scan/dashboard/stats
```

## Example stored document

```json
{
  "scan_id": "f47ac10b-58cc-4372-a567-0e02b2c3d479",
  "source_type": "file",
  "language": "c",
  "filename": "example.c",
  "code": "#include <string.h>\nvoid f() { char b[8]; strcpy(b, input); }",
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
        "line": 2,
        "severity": "HIGH",
        "code": "strcpy(b, input);"
      }
    ]
  },
  "metadata": {
    "model_name": "microsoft/codebert-base",
    "model_version": "best_codebert_linevul.pt",
    "threshold": 0.8,
    "checkpoint": "best_codebert_linevul.pt"
  },
  "created_at": "2026-05-26T02:00:00+00:00"
}
```

## Best practices

- Never commit Atlas credentials to git.
- Use `USE_IN_MEMORY_REPOSITORY=true` only for local demos without MongoDB.
- Keep source code as UTF-8 text; the API rejects oversized payloads.
- Use server-side history filters in production instead of loading all records to the client.
- Rotate database passwords and restrict Atlas IP allowlists in production.
