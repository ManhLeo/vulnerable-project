# Vulnerability Detection API (Backend)

FastAPI service that analyzes **C / C++** source code using:

1. **AI inference** — `microsoft/codebert-base` with optional local `.pt` checkpoints  
2. **Pattern analysis** — regex rules (e.g. `strcpy`, `gets`, `system`) with severity and risk scoring  
3. **Persistence** — MongoDB (`Motor`) or in-memory repository for development  

## Architecture

```text
app/
├── api/routes/       # HTTP handlers (thin)
├── services/         # Business workflows
├── ai/               # Model load, preprocess, inference
├── analysis/         # Pattern detection, risk scoring
├── db/               # Repositories + document mapping
├── models/           # Pydantic domain models (scan documents)
├── core/             # Config, database manager, exceptions, limiter
└── main.py           # App factory, lifespan, middleware
```

Startup (`lifespan`): connect MongoDB (unless in-memory) → ensure indexes → load ML model.  
Shutdown: unload model → disconnect MongoDB.

## Requirements

- Python **3.10+**
- pip packages in [requirements.txt](requirements.txt)
- Optional: CUDA if `MODEL_DEVICE` is not `cpu` and GPU is available

## Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Edit `.env`, then run:

```bash
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

Interactive API: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `Vulnerability Detection API` | Service title |
| `APP_ENV` | `development` | Environment name |
| `APP_DEBUG` | `true` | FastAPI debug |
| `MONGODB_URL` | `mongodb://localhost:27017` | MongoDB URI (alias: `MONGODB_URI`) |
| `MONGODB_DB_NAME` | `vuln_scanner` | Database name |
| `MONGODB_SCANS_COLLECTION` | `scans` | Collection for scan documents |
| `USE_IN_MEMORY_REPOSITORY` | `false` | `true` = no MongoDB, data lost on restart |
| `JWT_SECRET_KEY` | development default | JWT signing secret. Required to be non-default in production. |
| `MODEL_NAME_OR_PATH` | `microsoft/codebert-base` | Hugging Face model id or local path |
| `MODEL_DEVICE` | `cpu` | `cpu` or `cuda` (uses GPU if available) |
| `MODEL_VULNERABILITY_THRESHOLD` | `0.8` | Score threshold for ML “vulnerable” flag |
| `ADMIN_EMAIL` | | Optional default admin email. If set, an admin account is created/promoted on startup when no admin exists. |
| `ADMIN_PASSWORD` | | Optional default admin password. Must satisfy the password policy if `ADMIN_EMAIL` is set. |
| `MAX_UPLOAD_SIZE_BYTES` | `5242880` | Max upload size (5 MB) |
| `CORS_ALLOWED_ORIGINS_RAW` | `http://localhost:3000` | Comma-separated origins |
| `LOG_LEVEL` | `INFO` | Logging level |

See [.env.example](.env.example) for a starter file.

### MongoDB Atlas

1. Create cluster and database user.  
2. Set `MONGODB_URL` and `USE_IN_MEMORY_REPOSITORY=false`.  
3. Create indexes:

```bash
python scripts/mongodb_create_indexes.py
```

Full guide: [../docs/mongodb_atlas_setup.md](../docs/mongodb_atlas_setup.md)

### In-memory mode

```powershell
# Windows
$env:USE_IN_MEMORY_REPOSITORY="true"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

```bash
# macOS / Linux
USE_IN_MEMORY_REPOSITORY=true python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

## Model checkpoints

Place Hugging Face base files and trained checkpoints under:

```text
backend/models/codebert-base/
├── config.json          # (optional, from HF)
├── *.pt                 # checkpoint files
```

Default active checkpoint is configured in `app/ai/model_manager.py`.  
List and switch checkpoints via:

- `GET /api/v1/model/info`
- `POST /api/v1/model/select` — body: `{ "checkpoint_name": "best_codebert_linevul.pt" }`

## API (`/api/v1`)

| Method | Path | Notes |
|--------|------|--------|
| GET | `/health` | Health check |
| POST | `/scan/code` | JSON: `{ "source_code", "language" }` — rate limited |
| POST | `/scan/file` | multipart: `file`, optional `language` |
| GET | `/scan/history` | Query: `page`, `limit`, `filename`, `language`, `risk_level`, `is_vulnerable`, `search` |
| GET | `/scan/stats` | Aggregate scan stats scoped to current user; admins see all |
| GET | `/scan/{record_id}` | Full scan including `source_code` |
| DELETE | `/scan/{record_id}` | Remove scan |
| GET | `/model/info` | Model load state and checkpoints |
| POST | `/model/select` | Switch checkpoint |
| GET | `/admin/stats` | Admin-only system-wide stats |

### Supported inputs

- **Languages:** `c`, `cpp` (aliases: `c++`, `c_cpp`, `.h` → `c`, `.hpp` → `cpp`)
- **File extensions:** `.c`, `.cpp`, `.h`, `.hpp`

### Response envelope

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
```

## Scan pipeline (summary)

1. Validate language and sanitize source size.  
2. Run CodeBERT inference → `is_vulnerable`, `confidence`.  
3. Run pattern detector → findings with line + severity.  
4. Compute `risk_score` / `risk_level`; elevate verdict if HIGH/CRITICAL findings exist.  
5. Persist `ScanCreate` document and return summary + `scan_id`.

## Tests

```bash
# from backend/
python -m compileall -q app
pytest -q
```

Default pytest collection also includes root-level lightweight tests. Integration scripts that require a running server remain manual: `tests/api_validation.py`, `tests/explainability_validation.py`.

## Production security notes

- Set `APP_ENV=production`.
- Set `JWT_SECRET_KEY` to a strong non-default secret; production startup fails if the development default is used.
- Keep `.env.production` untracked. If it was added to git before the ignore rule existed, remove it from the index with `git rm --cached backend/.env.production`.

## Docker

See [Dockerfile](Dockerfile) if container deployment is configured.

## Related docs

- [../README.md](../README.md) — monorepo overview  
- [../docs/mongodb_atlas_setup.md](../docs/mongodb_atlas_setup.md) — Atlas setup  
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) — implementation audit (internal)
