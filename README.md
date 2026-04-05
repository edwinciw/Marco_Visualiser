# Macroeconomic visualiser — structured build plan

Create an app to visualise macroeconomic metrics (Vue SPA, Flask API, Docker).

---

## 1. Architecture (one sentence)

**Vue SPA** talks to a **Flask JSON API** over HTTP; **PostgreSQL** (or SQLite for dev) holds users, preferences, and series; **Docker Compose** runs frontend build + backend + DB with env-based config.

---

## 2. Data layer (GDP per capita, CPI/HICP, etc.)

- **Choose sources** (e.g. World Bank, Eurostat, OECD, national stats). Note licence and refresh rules in the README.
- **Align identifiers**: keep ISO3 for countries and stable metric codes (`Metric.code` — e.g. `gdp_pc`, `cpi_hicp`).
- **Ingestion**: small Python script or Flask CLI command that reads CSV/API → upserts `countries`, `metrics`, `observations` (idempotent on `(country, metric, period)`).
- **Document periods**: `period` strings are lexicographically sortable (`YYYY`, `YYYY-Qn`); document the convention so the UI and filters stay consistent.
- **Optional**: scheduled job (cron in container or external) to refresh data; log `ingested_at` (already on `Observation`).

---

## 3. Backend (Flask) — extend what you have

### Core API

- Keep `/api/health`, `/api/countries`, `/api/metrics`, `/api/series` — they already support multi-country, multi-metric, and date range.

### Auth (email login)

- Add routes: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.
- Store **password hash** only (e.g. `werkzeug.security` or argon2).
- Use **HTTP-only cookies** with a signed session, or **JWT** in cookies/Authorization header; prefer cookies + CSRF for cookie-based SPAs.
- Tighten **CORS**: allow only your Vue origin in production, not `*`, when cookies are used.

### Saved dashboards

- Use `UserPreferences.preferences` JSON to store layout: e.g. list of panels `{ id, title, countryIso3[], metricCodes[], periodFrom, periodTo }`.
- Add `GET` / `PATCH /api/me/preferences` (authenticated) to read/update that blob.
- Later, if layouts grow complex, normalize to a `dashboards` table; JSON is fine to start.

### Production hardening

- Env `SECRET_KEY`, rate limits on login, validation on query params, optional pagination if series payloads get huge.

---

## 4. Frontend (Vue)

- **Scaffold**: Vue 3 + Vite + TypeScript (optional but recommended), router, Pinia (or Vuex) for auth and dashboard state.
- **HTTP client**: `fetch` or Axios with `credentials: 'include'` if you use session cookies.
- **Charts**: ECharts, Chart.js, or Plotly — pick one; for multiple subplots, ECharts grid or small-multiples (one chart component per panel) works well.

### Feature mapping

- **Time series**: one reusable `TimeSeriesChart` fed by `/api/series`.
- **Filters**: multiselect for countries and metrics; date range (map to `period_from` / `period_to`).
- **Dashboard**: “Add panel” creates a card with its own country/metric/range (or inherit global filters — decide one pattern and stick to it).
- **Persistence**: on Save, `PATCH` preferences JSON; on load, restore panels and refetch series.
- **UX**: loading and empty states, error toasts from API `4xx`/`5xx`, responsive grid for panels.

---

## 5. Docker

- **Backend image**: Python slim, install `requirements.txt`, gunicorn (or waitress on Windows-friendly setups) serving `app:app`, non-root user.
- **Frontend image**: multi-stage build — `npm run build`, serve static files with nginx, or dev-only mount with Vite behind Compose.
- **Compose**: services `api`, `web` (nginx or dev server), `db` (Postgres recommended for multi-user auth); shared network; volumes for DB and optional SQLite if you stay on SQLite for a single-node demo.
- **Environment**: `DATABASE_URL`, `SECRET_KEY`, `VITE_API_BASE_URL` (or build-time API URL), documented in `.env.example`.

---

## 6. Implementation order (constructive sequence)

| Phase | What to build |
|-------|----------------|
| **A** | Seed DB + ingestion script for 2–3 countries and metrics (GDP per capita, CPI/HICP). Verify `/api/series` in browser or curl. |
| **B** | Vue app: login page stub + chart page calling `/api/*` with filters (no auth yet). |
| **C** | Flask auth + protected `GET`/`PATCH /api/me/preferences`; Vue login flow and storing JWT/session. |
| **D** | Dashboard builder: add/remove panels, each with series; save/load from preferences. |
| **E** | Dockerfiles + Compose; switch CORS and API URL for prod. |
| **F** | Tests: API integration tests for auth and series; minimal E2E for “login → see chart”. |

---

## 7. README sections worth including

- **Prerequisites**: Docker, Node, Python versions.
- **Quick start**: `docker compose up`, or local `flask run` + `npm run dev`.
- **API summary**: query params for `/api/series` (matches your existing contract).
- **Data refresh**: how to run the ingest script and where files live.
- **Security**: never commit `.env`; production `SECRET_KEY` and HTTPS.

---

## 8. Optional enhancements (after MVP)

- Alembic migrations instead of only `db.create_all()`.
- Admin-only upload endpoint for CSV.
- Export chart as PNG/PDF.
- Public read-only mode vs logged-in “save layout”.
