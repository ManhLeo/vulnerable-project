# AI-Powered Source Code Vulnerability Detection Platform

An enterprise-grade software vulnerability assessment and triage platform. The system uses a deep learning model (`microsoft/codebert-base`) combined with deterministic rules to identify, classify, and explain vulnerabilities in source code (`Python`, `C`, `C++`, `Java`).

Designed with a high-fidelity SaaS aesthetic (inspired by *Linear*, *Vercel*, and *Snyk*), this project provides a unified dashboard, an interactive code playground with real-time Monaco highlight decorations, and a paginated historic scan audit trail.

---

## 🏗️ System Architecture & Stack

The platform is designed under a decoupled, strict tier-based architecture following **Clean Architecture** patterns:

### Backend (`/backend`)
*   **FastAPI**: Modern, asynchronous Python web framework with centralized exception handling and type-safe response schemas.
*   **AI Engine**: Integrates a `microsoft/codebert-base` model optimized via local checkpoint checking for fast cold-starts.
*   **Database (Repository Pattern)**: Asynchronous MongoDB abstraction powered by `motor`, with built-in in-memory fallback repositories (`USE_IN_MEMORY_REPOSITORY='true'`) for portable local execution.
*   **Lifespan Management**: Fully modernized startup/shutdown event tracking using modern Python context managers.

### Frontend (`/frontend`)
*   **Next.js (App Router)**: Fast, React-based web app compiler using TypeScript in strict mode.
*   **TailwindCSS**: Utilitarian design system providing precise styling tokens and absolute visual consistency.
*   **Zustand**: High-performance, lightweight state management layer synchronizing active code, file streams, and selected findings.
*   **Monaco Editor**: Embedded lightweight code editor rendering active line highlights and colored gutter markers matching identified vulnerabilities.

---

## 🎨 Key Features & Redesigned Experiences

1.  **Unified SecOps Dashboard**:
    *   **Stat Cards**: Monospaced metrics for scans, detection ratios, and average AI model confidence.
    *   **Risk Distribution**: Fills the layout width using a beautiful horizontal CSS stacked bar segment with contextual details.
    *   **Recent Scans & Activity Timeline**: Features pulsing live active indicators and high-density, interactive data tables.
2.  **Scan Workspace & Monaco Playground**:
    *   Left-hand interactive Monaco editor displaying line numbers, file upload inputs, and language dropdown options.
    *   Selected findings list synchronized dynamically with editor highlights. Clicking finding rows triggers soft vertical scroll focus.
3.  **Enterprise Scan History**:
    *   Inline, flat toolbar housing filename search filters, risk selectors, and safe/vulnerable status options.
    *   Interactive pagination bar displaying page shortcuts, custom range info, and smart filter resets.
4.  **Premium UX Polish**:
    *   Fully integrated CSS shimmer loaders and skeleton tables ensuring zero layout shift (CLS).
    *   High-contrast WCAG AA accessible badges, focus-visible outlines for keyboard users, and smooth 150ms transitions.

---

## 🚀 Getting Started

### 1. Prerequisites
Ensure you have the following installed locally:
*   Python 3.10+
*   Node.js 18+ (with npm)
*   MongoDB (optional - if running with live database)

---

### 2. Backend Setup
1.  Navigate to the backend folder:
    ```bash
    cd backend
    ```
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Choose your running mode:
    *   **In-Memory Mode** (No MongoDB needed, perfect for local trial):
        *   **Windows**:
            ```powershell
            $env:USE_IN_MEMORY_REPOSITORY="true"
            python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
            ```
        *   **macOS / Linux / Git Bash**:
            ```bash
            USE_IN_MEMORY_REPOSITORY=true python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
            ```
    *   **Database Mode** (Requires local/remote MongoDB):
        Set up environment variables in `.env` and start the server:
        ```bash
        python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
        ```

---

### 3. Frontend Setup
1.  Navigate to the frontend folder:
    ```bash
    cd frontend
    ```
2.  Install packages:
    ```bash
    npm install
    ```
3.  Start the development server:
    ```bash
    npm run dev
    ```
    Open `http://localhost:3000` to access the platform.

#### 💡 Dev Cache Issue (404 Assets Error)
If you run `npm run build` while your development server (`npm run dev`) is active, Next.js will overwrite the cached server manifests. To clean it up:
1.  Stop the terminal runner (`Ctrl + C`).
2.  Clear the Next cache:
    *   **Windows**: `rd /s /q .next`
    *   **macOS / Linux**: `rm -rf .next`
3.  Run again: `npm run dev`.

---

## 📂 Git & Version Control Guidelines

This repository has a pre-configured `.gitignore` file that safely shields your version history from heavy files, binary binaries, local variables, and compilation outputs.

Before running `git commit`, verify that git ignores heavy files by executing:
```bash
git status
```

### Initial Commit Steps
To save your current production-ready platform state:
```bash
# 1. Add all project files
git add .

# 2. Commit the clean baseline
git commit -m "feat: complete enterprise-grade vulnerability triage redesign and API integration"

# 3. Add your remote origin and push
# git remote add origin <your-repo-url>
# git branch -M main
# git push -u origin main
```
