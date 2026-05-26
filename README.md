# AI-Powered Source Code Vulnerability Detection

Monorepo for scanning **C / C++** source code with a hybrid pipeline: **CodeBERT inference** plus **regex-based pattern detection**. Results include vulnerability verdict, confidence, risk level, line-level findings, and persisted scan history.

| Layer | Stack |
|-------|--------|
| Backend | FastAPI, PyTorch, Transformers, Motor (MongoDB) |
| Frontend | Next.js 14 (App Router), TypeScript, TanStack Query, Zustand, Monaco Editor |
| Storage | MongoDB Atlas (default) or in-memory repository (local dev) |

## Repository layout

```text
.
├── backend/          # FastAPI API + AI + analysis + persistence
├── frontend/         # Next.js UI (workspace, dashboard, history)
├── docs/             # Architecture, API, MongoDB setup guides
└── README.md
```

Detailed setup: [backend/README.md](backend/README.md) · [frontend/README.md](frontend/README.md) · [docs/mongodb_atlas_setup.md](docs/mongodb_atlas_setup.md)

## Features

- **Scan workspace** — paste code or upload `.c` / `.cpp` / `.h` / `.hpp` (max 5 MB)
- **Model selection** — switch CodeBERT checkpoints at runtime (`/api/v1/model/select`)
- **Explainability** — findings with severity, line number, and Monaco gutter highlights
- **Dashboard** — aggregate stats and risk distribution from stored scans
- **Scan history** — paginated list with filters; records survive server restarts when using MongoDB

## Quick start

### Prerequisites

- Python **3.10+**
- Node.js **18+**
- MongoDB (optional if using in-memory mode)

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env   # then edit values
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

**In-memory mode** (no MongoDB):

```bash
# Windows PowerShell
$env:USE_IN_MEMORY_REPOSITORY="true"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

API docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### 2. Frontend

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

## Persistence

| `USE_IN_MEMORY_REPOSITORY` | Scan history after server restart |
|----------------------------|-----------------------------------|
| `false` (default) | **Kept** in MongoDB |
| `true` | **Lost** (RAM only) |

Frontend workspace state (`latestResult` in Zustand) is browser-only; use **Scan History** or `GET /api/v1/scan/{id}` to reload saved scans.

## API overview

Base path: `/api/v1`

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Service health |
| POST | `/scan/code` | Analyze pasted source |
| POST | `/scan/file` | Analyze uploaded file |
| GET | `/scan/history` | Paginated history + filters |
| GET | `/scan/dashboard/stats` | Dashboard aggregates |
| GET | `/scan/{record_id}` | Single scan detail |
| DELETE | `/scan/{record_id}` | Delete scan |
| GET | `/model/info` | Model / checkpoint status |
| POST | `/model/select` | Switch checkpoint |

Rate limit: **10 requests/minute** on scan endpoints.

## UI routes

| Route | Purpose |
|-------|---------|
| `/` | Scan workspace |
| `/dashboard` | Security overview |
| `/scan/history` | Historic scans |
| `/scan/result` | Detailed report (from store or navigation) |

## Documentation

- [docs/mongodb_atlas_setup.md](docs/mongodb_atlas_setup.md) — Atlas cluster, env vars, indexes
- [docs/09_project_structure.md](docs/09_project_structure.md) — intended project layout

## Security notes

- Do not commit `backend/.env` or secrets; use `.env.example` as a template.
- Restrict MongoDB Atlas network access in production.
- Uploaded source may be stored in MongoDB when persistence is enabled.

## License

See repository license file if present.
