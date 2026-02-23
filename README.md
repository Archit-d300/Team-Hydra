# 🚰 Drought Warning & Tanker Management System

**PRERNA 18.0 · SDG 6 — Clean Water & Sanitation · Ramdeobaba University**

A real-time drought monitoring and water tanker allocation system for Vidarbha, Maharashtra.

---

## ✅ Currently Completed Features

- **Dashboard** — Live summary of village water stress, tanker counts, severity chart, allocation stats
- **Village Map** — Google Maps with color-coded severity markers (falls back to table view without API key)
- **Allocations** — Priority-based tanker dispatch table with today's deployment plan
- **Stress Calculation** — Water Stress Index (0–10) algorithm using rainfall deviation + groundwater levels
- **Tanker Allocator** — Priority queue algorithm: CRITICAL → HIGH → MEDIUM → LOW

---

## 🌐 Functional Entry URIs (Frontend Routes)

| Path | Description |
|------|-------------|
| `/` | Dashboard — overview, stress chart, allocation controls |
| `/map` | Village Risk Map (requires `VITE_GOOGLE_MAPS_KEY`) |
| `/allocations` | Today's tanker deployment plan |

---

## 🔌 Backend API Routes (FastAPI · Port 8000)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/dashboard/` | Dashboard summary (villages, tankers, stress) |
| GET | `/api/villages/` | All villages with latest stress info |
| POST | `/api/villages/calculate-all-stress` | Recalculate stress for all villages |
| GET | `/api/villages/{id}/stress` | Stress for a single village |
| POST | `/api/villages/seed` | Seed test village data |
| GET | `/api/tankers/` | All tankers |
| POST | `/api/tankers/seed` | Seed 12 test tankers |
| POST | `/api/tankers/allocate` | Run allocation algorithm |
| GET | `/api/tankers/allocations` | Today's allocations |
| GET | `/docs` | Swagger API docs |

---

## 🚀 Running Locally

### Prerequisites
- Node.js 18+
- Python 3.10+
- Supabase project with tables: `villages`, `tankers`, `water_stress_index`, `tanker_allocations`, `rainfall_data`, `groundwater_levels`

### 1. Backend Setup
```bash
cd backend
cp .env.example .env
# Edit .env with your SUPABASE_URL and SUPABASE_KEY
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### 2. Frontend Setup
```bash
# In project root
cp .env.example .env
# Optional: Add VITE_GOOGLE_MAPS_KEY for the map page
npm install
npm run dev
# Opens at http://localhost:3000
```

### 3. Seed Data (First Time)
Call these endpoints once to populate the database:
1. `POST /api/villages/seed` — Adds 8 Vidarbha villages with mock rainfall/groundwater data
2. `POST /api/tankers/seed` — Adds 12 tankers

---

## 🗂️ Data Architecture

### Data Models
| Table | Fields |
|-------|--------|
| `villages` | id, name, district, taluka, population, lat, lng |
| `tankers` | id, registration_no, capacity_liters, current_district, status |
| `rainfall_data` | village_id, recorded_date, rainfall_mm, normal_rainfall_mm |
| `groundwater_levels` | village_id, recorded_date, level_meters, safe_threshold_meters |
| `water_stress_index` | village_id, calculated_date, stress_score, severity, tankers_needed |
| `tanker_allocations` | tanker_id, village_id, allocated_date, status |

### Storage
- **Supabase (PostgreSQL)** — All data persistence

### Stress Algorithm
```
Water Stress Score (0–10) =
  Rainfall Deviation Score (0–5) +   # How far below normal rainfall is
  Groundwater Danger Score (0–5)     # How far below safe threshold groundwater is

Severity:  ≥8 = CRITICAL | ≥6 = HIGH | ≥4 = MEDIUM | <4 = LOW
Tankers:   Only HIGH and CRITICAL villages receive tankers
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React 19, Vite 7, Tailwind CSS v4, Recharts, React Router DOM v7 |
| Maps | Google Maps JavaScript API (`@react-google-maps/api`) |
| HTTP Client | Axios |
| Backend | FastAPI (Python), Uvicorn |
| Database | Supabase (PostgreSQL) |
| Dev Proxy | Vite proxy → FastAPI at port 8000 |

---

## 🔧 Environment Variables

### Frontend (`.env`)
```
VITE_API_URL=          # Leave empty for local dev (uses Vite proxy)
VITE_GOOGLE_MAPS_KEY=  # Your Google Maps API key
```

### Backend (`backend/.env`)
```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_key
```

---

## ⚠️ Features Not Yet Implemented

- Historical trend charts (rainfall over time per village)
- Per-village stress detail page
- Tanker GPS tracking / live updates
- User authentication / admin panel
- Mobile-responsive map controls
- Automated daily stress recalculation (cron job)
- Email/SMS alerts for critical villages

## 💡 Recommended Next Steps

1. Add `VITE_GOOGLE_MAPS_KEY` to enable the interactive map
2. Set up Supabase and create the DB tables
3. Seed the database using the `/seed` endpoints
4. Click "Recalculate & Allocate" on the dashboard to run the algorithm
5. Consider adding WebSocket for real-time updates
