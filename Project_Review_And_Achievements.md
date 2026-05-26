# Báo cáo đánh giá & thành tựu — Vulnerable Project

**Ngày cập nhật:** Tháng 5/2026  
**Phạm vi:** Monorepo `backend/` + `frontend/` + tài liệu vận hành  
**Mục tiêu:** Tổng hợp tính năng đã triển khai, đánh giá chất lượng mã, và ghi nhận khoảng trống / việc cần làm tiếp.

---

## 1. Tóm tắt trạng thái triển khai

| Hạng mục | Trạng thái |
|----------|------------|
| Quét mã C/C++ (paste + upload) | Hoàn thành |
| AI CodeBERT + pattern rules | Hoàn thành |
| Lưu lịch sử scan (MongoDB Atlas) | Hoàn thành |
| Chế độ in-memory (dev không MongoDB) | Hoàn thành |
| Đổi checkpoint model runtime | Hoàn thành (API + UI selector) |
| Dashboard & lịch sử có filter | Hoàn thành (UI; dashboard stats client-side) |
| Xóa bản ghi scan | API hoàn thành; **chưa có UI** |
| README monorepo / backend / frontend | Đã cập nhật (05/2026) |

**Ngôn ngữ hỗ trợ thực tế:** `c`, `cpp` (file `.c`, `.cpp`, `.h`, `.hpp`). README cũ từng ghi Python/Java — **không còn đúng** với pipeline hiện tại.

---

## 2. Thành tựu đã hoàn thiện

### 2.1 Backend (FastAPI)

**Kiến trúc tầng**

- `api/routes` → `services` → `ai` / `analysis` → `db/repositories`
- Dependency injection repository qua `app/api/dependencies.py`
- `lifespan` trong `main.py`: MongoDB (hoặc bỏ qua nếu in-memory) → `ensure_indexes()` → load model → shutdown ngược lại

**AI inference**

- `model_manager.py`: load `microsoft/codebert-base`, checkpoint `.pt` từ `backend/models/codebert-base/`
- Hỗ trợ đổi checkpoint: `POST /api/v1/model/select`
- `inference.py`: forward pass trong thread pool (`asyncio.to_thread`), ngưỡng `MODEL_VULNERABILITY_THRESHOLD`

**Phân tích lai (hybrid)**

- Pattern regex: `strcpy`, `gets`, `system`, `sprintf`, … (`analysis/patterns.py`)
- Gộp verdict ML + rule: nếu có finding `HIGH`/`CRITICAL` → `is_vulnerable = true`
- `risk_score` + `risk_level` (`analysis/risk.py`, `severity.py`)

**Persistence & schema**

- `DatabaseManager` (`core/database.py`): ping Atlas/local, pool, tạo index trên collection `scans`
- Domain models (`models/scan_models.py`): `ScanCreate`, `ScanDocument`, `ScanHistoryFilters`, `DashboardStats`, …
- `document_mapper.py`: map domain ↔ document MongoDB (nested `prediction`, `analysis`, `metadata`)
- `ScanRepository` + `InMemoryScanRepository`: CRUD, history **có filter** (`filename`, `language`, `risk_level`, `is_vulnerable`, `search`)
- `db/security.py`: sanitize source, regex filter an toàn, validate `scan_id`
- Script index: `scripts/mongodb_create_indexes.py`
- Hướng dẫn Atlas: `docs/mongodb_atlas_setup.md`

**API (`/api/v1`)**

| Method | Path | Ghi chú |
|--------|------|---------|
| GET | `/health` | Health check |
| POST | `/scan/code` | Rate limit 10/phút |
| POST | `/scan/file` | Upload multipart |
| GET | `/scan/history` | Pagination + filters |
| GET | `/scan/dashboard/stats` | Thống kê server-side |
| GET | `/scan/{record_id}` | Chi tiết + source |
| DELETE | `/scan/{record_id}` | Xóa bản ghi |
| GET | `/model/info` | Checkpoint đang dùng |
| POST | `/model/select` | Đổi checkpoint |

**Vận hành & bảo mật cơ bản**

- CORS, request logging (UUID), SlowAPI rate limit
- Exception handlers chuẩn `error_response()` + mã `error_code`
- Giới hạn upload 5 MB; extension whitelist

### 2.2 Frontend (Next.js 14)

**Trang & luồng**

| Route | Chức năng |
|-------|-----------|
| `/` | Scan workspace: Monaco, upload, language, model selector, findings |
| `/dashboard` | Stat cards, risk distribution, recent scans, activity feed |
| `/scan/history` | Bảng lịch sử, filter, pagination |
| `/scan/result` | Báo cáo chi tiết từ Zustand |

**Kỹ thuật**

- Zustand (`scan-store`): code, language, `latestResult`, finding selection
- TanStack Query: scan mutations, history query, model info / select
- Axios client + chuẩn hóa lỗi API (`lib/api/client.ts`)
- Monaco: highlight dòng theo findings
- Mở lại scan từ history: `getScanRecord(id)` → hydrate store (recent list / history table)

**Theme & UX**

- App shell, sidebar, design tokens CSS, skeleton loaders

### 2.3 Tài liệu & vận hành

- [README.md](README.md) — tổng quan monorepo, persistence, API/UI routes
- [backend/README.md](backend/README.md) — env, model, API chi tiết
- [frontend/README.md](frontend/README.md) — setup, cấu trúc `src/`
- [docs/mongodb_atlas_setup.md](docs/mongodb_atlas_setup.md) — Atlas + indexes

**Persistence sau restart server**

- `USE_IN_MEMORY_REPOSITORY=false` + MongoDB Atlas → **lịch sử scan vẫn còn**
- `USE_IN_MEMORY_REPOSITORY=true` → mất khi tắt process
- State workspace trên browser (Zustand) → mất khi refresh; load lại qua History/API

---

## 3. Đánh giá chất lượng mã nguồn

### 3.1 Điểm mạnh

- **Backend:** Type hints nhất quán; tách repository/domain mapper rõ; filter history đã dùng cùng query cho `find` và `count` (không còn lỗi count toàn collection khi filter).
- **Frontend:** Cấu trúc `features/` + `services/` + `hooks/` dễ đọc; ESLint sạch trong các lần kiểm tra trước.
- **Hợp đồng API:** Envelope `{ status, data, message }` / `{ status, message, error_code }` thống nhất.

### 3.2 Điểm cần cải thiện

- Một số module legacy / trùng vai trò (ví dụ `app/db/mongo.py` chỉ re-export `database_manager`).
- Response OpenAPI chưa gắn `response_model` ở routes → Swagger kém chi tiết.
- Dashboard frontend vẫn **tổng hợp từ history client-side** thay vì gọi `GET /scan/dashboard/stats` (API backend đã có).

---

## 4. Mã / module dư thừa hoặc chưa dùng hết

### 4.1 Backend

| Thành phần | Trạng thái | Ghi chú |
|------------|------------|---------|
| `app/schemas/health.py`, `model.py`, phần `common.py`, `scan.py` (response DTO) | **Ít / không dùng** | Routes trả `success_response(dict)`; chỉ `ScanCodeRequest` trong `schemas/scan.py` được import |
| `DEFAULT_SUCCESS_MESSAGE`, `INTERNAL_SERVER_ERROR_MESSAGE` trong `constants.py` | **Có thể chưa dùng** | `response.py` vẫn hard-code message |
| `ValidationException` trong `exceptions.py` | **Không dùng** | Đã có handler `RequestValidationError` |
| `app_host`, `app_port` trong `config.py` | **Không đọc khi chạy uvicorn CLI** | Host/port lấy từ lệnh terminal |
| `app/repositories/scan_repository.py` | Re-export | Entry point kiến trúc; implementation thật ở `db/repositories/` |

**Đã khắc phục so với báo cáo trước**

- Domain models `app/models/scan_models.py` **đang được dùng** bởi service + repository (không phải dead code).
- `list_scan_history` đã hỗ trợ filter đúng qua `ScanHistoryFilters` + `_build_history_query`.

### 4.2 Frontend

- Không ghi nhận dead code đáng kể trong lần rà soát trước.
- **Thiếu tích hợp:** `DELETE /scan/{id}`, `GET /scan/dashboard/stats` chưa có service/hook/UI.

---

## 5. Khoảng trống chức năng (gaps)

| Gap | Mức độ | Mô tả |
|-----|--------|--------|
| UI xóa scan | Trung bình | API có; frontend chưa |
| Dashboard dùng API stats | Thấp | Trùng logic client vs server |
| Mở rộng ngôn ngữ (Python/Java) | Roadmap | Pattern/rules chưa có cho ngôn ngữ khác |
| Auth / multi-user | Roadmap | Chưa có |
| `.env.example` backend | Thấp | Template nên có trong repo (tránh commit `.env`) |

---

## 6. Hành động đề xuất (ưu tiên)

1. **Dọn hoặc tận dụng `app/schemas/` response models** — gắn `response_model` trên routes để OpenAPI chính xác, hoặc xóa class không dùng.
2. **Frontend:** gọi `GET /api/v1/scan/dashboard/stats` trên Dashboard; thêm nút xóa + `DELETE` trên History.
3. **Dùng hằng `constants.py`** trong `response.py` / `exceptions.py` thay vì string lặp.
4. **Bảo mật:** không commit `backend/.env`; rotate credential nếu từng lộ; siết IP whitelist Atlas ở production.
5. **Kiểm thử:** chạy `pytest` backend + smoke test upload/scan/history sau đổi MongoDB.

---

## 7. Kết luận

Dự án đã đạt **MVP end-to-end**: quét C/C++ bằng AI + rules, hiển thị explainability trên Monaco, lưu và xem lại lịch sử qua MongoDB Atlas, đổi checkpoint model từ UI. Kiến trúc backend được củng cố thêm lớp domain model và persistence an toàn hơn so với phiên bản “foundation” ban đầu.

Phần còn lại chủ yếu là **hoàn thiện tích hợp frontend** (stats API, delete), **dọn dead schema**, và **hardening** cho môi trường production.
