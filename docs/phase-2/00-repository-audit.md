# Repository Audit — Phase 2 Baseline

**Date:** 2026-08-04  
**Auditor:** Automated repository analysis  
**Commit baseline:** Pre-Phase 2 (no git repo initialised)

---

## 1. Current Architecture

```
hackathon-tracker/
├── @/                          # ⚠️ ORPHANED — shadcn/ui output mis-generated at repo root
│   └── components/ui/          # button, dialog, drawer, input, popover (NOT used by src/)
├── public/                     # Static assets (favicon.svg, icons.svg)
├── src/
│   ├── app/App.tsx             # Root component — renders AppRouter
│   ├── main.tsx                # Entry point — React 19 StrictMode
│   ├── components/
│   │   ├── layout/             # AppLayout, Sidebar, Topbar, CommandPalette
│   │   └── ui/                 # button.tsx (manual), glass-panel.tsx
│   ├── lib/utils.ts            # cn() helper (clsx + tailwind-merge)
│   ├── pages/                  # Dashboard.tsx, Placeholder.tsx
│   ├── router/index.tsx        # createBrowserRouter — 9 routes (1 real, 8 placeholder)
│   ├── store/                  # Zustand stores (hackathon, filter, history, ui)
│   ├── styles/                 # globals.css, cmdk.css
│   └── types/index.ts          # Full domain model (18 interfaces)
├── index.html                  # SPA entry
├── package.json                # npm project config
├── package-lock.json           # npm lockfile (confirms npm as package manager)
├── vite.config.ts              # Vite 8 + React plugin + path alias
├── tsconfig.json               # Project references (app + node)
├── tsconfig.app.json           # App TS config — @/* alias
├── tsconfig.node.json          # Node TS config — vite.config.ts only
├── tailwind.config.ts          # Tailwind v3 + shadcn theme tokens + animate plugin
├── postcss.config.js           # tailwindcss + autoprefixer
├── components.json             # shadcn/ui config (points to src/styles/globals.css)
├── .oxlintrc.json              # Oxlint config (react + typescript + oxc plugins)
└── .gitignore                  # Standard Vite gitignore
```

> [!IMPORTANT]
> **No backend, Docker, tests, CI configuration or environment files exist.** The Phase 1 description mentions "backend folders, Docker files, tests and configuration placeholders" but none were found in the repository.

---

## 2. Current Frontend Stack

| Component | Technology | Version |
|---|---|---|
| **Framework** | React | 19.2.8 |
| **Build tool** | Vite | 8.2.0 |
| **Language** | TypeScript | 6.0.2 |
| **Routing** | react-router-dom | 7.18.2 |
| **State management** | Zustand | 5.0.14 |
| **CSS framework** | Tailwind CSS | 3.4.19 |
| **CSS animations** | tailwindcss-animate | 1.0.7 |
| **Linter** | oxlint | 1.75.0 |
| **UI primitives** | Radix UI (dialog, popover, slot) | latest |
| **Charts** | Recharts | 3.10.1 |
| **Forms** | react-hook-form + @hookform/resolvers + Zod | latest |
| **Motion** | framer-motion | 12.43.0 |
| **Command palette** | cmdk | 1.1.1 |
| **Table** | @tanstack/react-table | 8.21.3 |
| **Virtual list** | @tanstack/react-virtual | 3.14.9 |
| **DnD** | @dnd-kit/core + sortable + utilities | latest |
| **Drawer** | vaul | 1.1.2 |
| **Toasts** | sonner | 2.0.7 |
| **Date utility** | date-fns | 4.4.0 |
| **CSV parsing** | papaparse | 5.5.4 |
| **Excel** | xlsx | 0.18.5 |
| **Resizable panels** | react-resizable-panels | 4.12.2 |
| **Package manager** | **npm** (confirmed by `package-lock.json`) | — |

---

## 3. Current Backend Stack

> [!CAUTION]
> **No backend exists.** There are no Python files, no `requirements.txt`, no FastAPI/Flask application, no `backend/` directory, no Alembic migrations, no database models, and no Docker configuration anywhere in the repository.

---

## 4. Database State

| Item | Status |
|---|---|
| PostgreSQL | ❌ Not configured |
| SQLAlchemy | ❌ Not present |
| Alembic migrations | ❌ Not present |
| Database models | ❌ Not present |
| Connection configuration | ❌ Not present |

**TypeScript domain model** exists in `src/types/index.ts` with 18 interfaces covering:
Workspace, User, Hackathon, Team, Project, Round, RoundProgress, Technology, ProjectTechnology, SubmissionLink, Deadline, Reward, Status, ApiKey, TeamMember, HackathonMentor, HackathonJudge, NormalizedState.

These will serve as the **reference schema** for backend models.

---

## 5. Authentication State

| Item | Status |
|---|---|
| JWT library (backend) | ❌ Not present |
| Password hashing (backend) | ❌ Not present |
| Auth routes (backend) | ❌ Not present |
| Auth context (frontend) | ❌ Not present |
| Auth store (frontend) | ❌ Not present |
| Login/Register pages | ❌ Not present |
| API client / interceptors | ❌ Not present |
| Protected routes | ❌ Not present |
| Token storage | ❌ Not present |

---

## 6. Working Modules

| Module | Path | Status |
|---|---|---|
| **Main entry** | `src/main.tsx` | ✅ Working |
| **App component** | `src/app/App.tsx` | ✅ Working |
| **Router** | `src/router/index.tsx` | ⚠️ Works but has unused `Outlet` import |
| **AppLayout** | `src/components/layout/AppLayout.tsx` | ✅ Working |
| **Sidebar** | `src/components/layout/Sidebar.tsx` | ✅ Working |
| **Topbar** | `src/components/layout/Topbar.tsx` | ✅ Working |
| **CommandPalette** | `src/components/layout/CommandPalette.tsx` | ✅ Working |
| **Button** | `src/components/ui/button.tsx` | ✅ Working (manual impl, no CVA) |
| **GlassPanel** | `src/components/ui/glass-panel.tsx` | ✅ Working |
| **cn() utility** | `src/lib/utils.ts` | ✅ Working |
| **UI Store** | `src/store/uiStore.ts` | ✅ Working (persisted) |
| **Filter Store** | `src/store/filterStore.ts` | ✅ Working (persisted) |
| **History Store** | `src/store/historyStore.ts` | ✅ Working |
| **Hackathon Store** | `src/store/hackathonStore.ts` | ✅ Working (in-memory only) |
| **Global CSS** | `src/styles/globals.css` | ✅ Working (light + dark tokens) |
| **CMDK CSS** | `src/styles/cmdk.css` | ✅ Working |
| **Type definitions** | `src/types/index.ts` | ✅ Working |
| **Dev server** | `npm run dev` (Vite) | ✅ Starts on localhost:5173 |

---

## 7. Placeholder Modules

| Module | Path | Nature |
|---|---|---|
| **Dashboard page** | `src/pages/Dashboard.tsx` | UI shell only — 3 static "Widget" placeholders, no data binding |
| **Placeholder page** | `src/pages/Placeholder.tsx` | Generic "coming soon" page used for 8 routes |
| **Hackathons route** | `/hackathons` | Points to `Placeholder` — no hackathon list or CRUD |
| **Calendar route** | `/calendar` | Placeholder |
| **Kanban route** | `/kanban` | Placeholder (out of Phase 2 scope) |
| **Analytics route** | `/analytics` | Placeholder (out of Phase 2 scope) |
| **Teams route** | `/teams` | Placeholder (out of Phase 2 scope) |
| **Projects route** | `/projects` | Placeholder (out of Phase 2 scope) |
| **Vault route** | `/vault` | Placeholder (out of Phase 2 scope) |
| **Settings route** | `/settings` | Placeholder |
| **Hackathon Store** | `src/store/hackathonStore.ts` | In-memory only — no API integration |

---

## 8. Broken Modules

### 8.1 `@/` Physical Directory (CRITICAL)

The repo root contains a literal `@/` directory with 5 shadcn/ui component files:
- `@/components/ui/button.tsx` — imports `class-variance-authority` (NOT installed)
- `@/components/ui/dialog.tsx`
- `@/components/ui/drawer.tsx` — has `"use client"` directive (Next.js artifact)
- `@/components/ui/input.tsx`
- `@/components/ui/popover.tsx`

**Problems:**
1. These files are **not inside `src/`** so they are not compiled by TypeScript or bundled by Vite
2. They import `@/lib/utils` expecting the Vite alias, but since they're outside `src/`, the alias does not resolve
3. `class-variance-authority` is not in `package.json` — `@/components/ui/button.tsx` will fail to compile
4. No source file in `src/` imports from these files — they are completely orphaned
5. The `@` folder was likely created by `shadcn/ui` init misinterpreting the `@` path alias as a physical directory

**Proposed fix:** Delete the entire `@/` directory. Move any needed components (dialog, drawer, input, popover) into `src/components/ui/` after adapting them to not use CVA, or install CVA.

### 8.2 TypeScript Build Failure

`npm run build` fails with two errors:

| Error | Cause | Fix |
|---|---|---|
| `TS5101: Option 'baseUrl' is deprecated` | TypeScript 6.0 deprecated `baseUrl` in `tsconfig.app.json` | Add `"ignoreDeprecations": "6.0"` to `compilerOptions` OR remove `baseUrl` and use `rootDirs` |
| `TS2769: manualChunks — 'vendor' does not exist in type 'ManualChunksFunction'` | Vite 8 / Rolldown changed `manualChunks` API — object syntax no longer valid | Convert `manualChunks` to a function or remove the config |

### 8.3 Lint Warnings

| Warning | File | Fix |
|---|---|---|
| `no-unused-vars: Outlet imported but never used` | `src/router/index.tsx:2` | Remove unused `Outlet` import |
| `only-export-components: buttonVariants exported alongside Button` | `@/components/ui/button.tsx:56` | This is in the orphaned `@` dir — will be resolved when deleted |

---

## 9. Missing Dependencies

| Dependency | Required By | Status |
|---|---|---|
| `class-variance-authority` | `@/components/ui/button.tsx` | ❌ Not installed (orphaned file) |
| `vitest` / test runner | No `test` script in package.json | ❌ Not installed |
| Backend framework (FastAPI) | Phase 2 requirement | ❌ Not installed |
| SQLAlchemy | Phase 2 requirement | ❌ Not installed |
| Alembic | Phase 2 requirement | ❌ Not installed |
| psycopg / asyncpg | Phase 2 requirement | ❌ Not installed |
| python-jose / PyJWT | Phase 2 requirement | ❌ Not installed |
| passlib / bcrypt | Phase 2 requirement | ❌ Not installed |
| axios / fetch wrapper | API client for frontend | ❌ Not present |

---

## 10. Environment Variables Required

No `.env`, `.env.example`, or `.env.local` files exist. The following will be needed for Phase 2:

### Frontend (`.env` / `.env.local`)
| Variable | Purpose |
|---|---|
| `VITE_API_BASE_URL` | Backend API endpoint (e.g., `http://localhost:8000/api/v1`) |

### Backend (`.env`)
| Variable | Purpose |
|---|---|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing secret |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | JWT token TTL |
| `CORS_ORIGINS` | Allowed frontend origins |

---

## 11. Existing Command Results

| # | Command | Result | Exit Code | Notes |
|---|---|---|---|---|
| 1 | `npm run lint` | ✅ Pass (2 warnings, 0 errors) | 0 | Unused `Outlet` import; CVA export warning in orphaned file |
| 2 | `npm run build` | ❌ Fail | 1 | TS5101 baseUrl deprecation + TS2769 manualChunks type mismatch |
| 3 | `npm run dev` | ✅ Pass | — | Vite 8.2.0 starts on localhost:5173 in ~1.7s |
| 4 | `npm ls class-variance-authority` | ❌ Empty | 1 | Package not installed |
| 5 | `npx tsc --version` | ✅ Pass | 0 | TypeScript 6.0.3 |
| 6 | Backend install/test | ⛔ N/A | — | No backend exists |
| 7 | Docker build | ⛔ N/A | — | No Docker files exist |
| 8 | `git add .` (parent dir) | ❌ Fail | 1 | No git repository initialised |

---

## 12. Security Concerns

1. **No git repository** — no version control, no ability to track changes or roll back
2. **No `.env.example`** — no template for required environment variables
3. **No `.gitignore` coverage for `.env`** — the current `.gitignore` does not explicitly exclude `.env` files (only `*.local`)
4. **Topbar shows hardcoded "ME" avatar** — no auth, anyone accessing the URL sees the same session
5. **No CORS configuration** — backend does not exist yet
6. **No CSP headers** — no Content-Security-Policy configured
7. **`xlsx` package** — SheetJS `xlsx` has known supply-chain concerns; evaluate if truly needed in Phase 2

---

## 13. Duplicate / Conflicting Architecture

| Issue | Details |
|---|---|
| **Duplicate Button component** | `src/components/ui/button.tsx` (manual, working) vs `@/components/ui/button.tsx` (shadcn/CVA, broken) |
| **Orphaned `@/` directory** | 5 shadcn/ui files outside `src/`, not bundled, importing missing dependency |
| **`components.json` alias mismatch** | Points `components` to `@/components` and `utils` to `@/lib/utils` — the `@` alias resolves to `src/` in Vite/TS but shadcn created a literal `@/` directory |
| **React import style** | Most files use `import React from 'react'` (legacy, unnecessary with jsx: react-jsx) |
| **No single API layer** | No `api/` or `services/` directory, no HTTP client configured |

---

## 14. Recommended Implementation Order

Based on the audit findings, Phase 2 should proceed in this dependency order:

1. **Fix broken build** — resolve TS deprecation and Vite manualChunks errors
2. **Clean up orphaned `@/` directory** — delete or relocate
3. **Initialise git repository** — version control before any further changes
4. **Create backend skeleton** — FastAPI + async SQLAlchemy + PostgreSQL
5. **Database models + Alembic migrations** — User, Workspace, Hackathon, Status
6. **Authentication backend** — registration, login, JWT, password hashing
7. **Hackathon CRUD API** — workspace-scoped endpoints
8. **Frontend API client** — configured axios/fetch with auth interceptors
9. **Frontend auth flow** — context, store, login/register pages, protected routes
10. **Frontend Hackathons page** — connected to real backend CRUD
11. **Dashboard statistics** — connected to real data aggregation endpoint
12. **Environment files** — `.env.example` for both frontend and backend
13. **Docker setup** — Dockerfiles + docker-compose for full-stack local dev
14. **Automated tests** — Vitest (frontend) + pytest (backend) + browser smoke tests
