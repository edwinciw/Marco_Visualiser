/**
 * JSON shapes returned by the Flask API (`/api/countries`, `/api/metrics`, `/api/series`).
 */

// --- Reference data: GET /api/countries ---

// Reference row from `countries` table.
export interface Country {
  id: number;
  iso3: string;
  name: string;
}

// --- Reference data: GET /api/metrics ---

// Reference row from `metrics` table; `code` is what `/api/series` expects.
export interface Metric {
  id: number;
  code: string;
  name: string;
  description: string | null;
  unit: string | null;
  frequency: string | null;
}

// --- Time series: GET /api/series ---

// One observation in a series bundle.
export interface SeriesPoint {
  period: string;
  value: number;
}

// One (country × metric) group with ordered points.
export interface SeriesBundle {
  country_iso3: string;
  metric_code: string;
  points: SeriesPoint[];
}

// Top-level body of GET `/api/series`.
export interface SeriesResponse {
  series: SeriesBundle[];
}

// --- Error responses (4xx from Flask) ---

// Flask often returns `{ "error": "..." }` on 4xx.
export interface ApiErrorBody {
  error?: string;
}
