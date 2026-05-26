# Vulnerability Detection UI (Frontend)

Next.js 14 application for the vulnerability detection platform: scan workspace (Monaco editor), dashboard analytics, and paginated scan history. Communicates with the FastAPI backend via REST (`/api/v1`).

## Stack

- **Next.js 14** — App Router, TypeScript  
- **TanStack Query** — server state, mutations, cache invalidation  
- **Zustand** — workspace state (code, language, latest result, selected finding)  
- **Monaco Editor** — code editing and finding line highlights  
- **Tailwind CSS** — layout and design tokens  
- **Axios** — HTTP client with normalized API errors  

## Requirements

- Node.js **18+**
- npm
- Backend running at `http://localhost:8000` (or custom base URL)

## Setup

```bash
cd frontend
npm install
cp .env.example .env.local
npm run dev
```

App URL: [http://localhost:3000](http://localhost:3000)

## Environment

| Variable | Required | Description |
|----------|----------|-------------|
| `NEXT_PUBLIC_API_BASE_URL` | Dev: optional (defaults to `http://localhost:8000`) | Backend origin |
| `NEXT_PUBLIC_API_BASE_URL` | Production: **required** | Must point to deployed API |

Example `.env.local`:

```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
```

## Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Development server (port 3000) |
| `npm run build` | Production build |
| `npm run start` | Serve production build |
| `npm run lint` | ESLint |
| `npm run typecheck` | `tsc --noEmit` |

## Routes

| Path | Component area | Description |
|------|----------------|-------------|
| `/` | `features/scan-workspace` | Paste/upload code, run scan, view findings |
| `/dashboard` | `features/scan-history` | Stats, risk distribution, recent activity |
| `/scan/history` | `features/scan-history` | Filterable paginated history |
| `/scan/result` | `features/scan-workspace` | Full report view from workspace state |

## Project structure

```text
src/
├── app/                    # Next.js pages (App Router)
├── components/             # Layout, UI primitives, providers
├── features/
│   ├── scan-workspace/     # Editor, upload, model selector, findings
│   └── scan-history/       # Dashboard, table, filters, pagination
├── hooks/                  # React Query mutations & queries
├── lib/
│   ├── api/client.ts       # Axios instance + error normalization
│   ├── store/scan-store.ts # Zustand workspace state
│   └── query/query-keys.ts
├── services/               # API functions (scan, model, health)
└── types/api.ts            # DTO types aligned with backend
```

## API integration

Services call the backend under `/api/v1`:

- `scan.service.ts` — `POST /scan/code`, `POST /scan/file`, `GET /scan/history`, `GET /scan/{id}`
- `model.service.ts` — `GET /model/info`, `POST /model/select`
- `health.service.ts` — `GET /health`

After a successful scan, history queries are invalidated so dashboard/history stay in sync.

## Workspace state

`scan-store` (Zustand) holds:

- Current editor `code` and `language`
- `latestResult` from the last scan (lost on full page reload unless re-fetched)
- `selectedFindingIndex` for Monaco sync

Persisted scans are always loaded from the backend via **Scan History** or `getScanRecord(id)`.

## Dev troubleshooting

If `npm run build` was run while `npm run dev` is active, Next.js cache can cause 404 assets:

```bash
# stop dev server first
# Windows
rd /s /q .next
# macOS / Linux
rm -rf .next
npm run dev
```

## Related docs

- [../README.md](../README.md) — monorepo quick start  
- [../backend/README.md](../backend/README.md) — API and env reference  
