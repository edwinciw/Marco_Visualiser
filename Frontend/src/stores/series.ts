// --- Dependencies ---
import { defineStore } from "pinia";
import { ref } from "vue";
import { apiFetch } from "@/api/client";
import type { SeriesBundle, SeriesResponse } from "@/api/types";

// --- Helpers (private to this module) ---

/**
 * Encode filter state as query string matching Flask’s repeated `country` / `metric` params.
 */
function buildQuery(params: {
  countries: string[];
  metrics: string[];
  periodFrom: string;
  periodTo: string;
}): string {
  const q = new URLSearchParams();
  for (const c of params.countries) q.append("country", c);
  for (const m of params.metrics) q.append("metric", m);
  if (params.periodFrom.trim()) q.set("period_from", params.periodFrom.trim());
  if (params.periodTo.trim()) q.set("period_to", params.periodTo.trim());
  return q.toString();
}

/**
 * Holds the latest `/api/series` response and request status for the chart view.
 */
export const useSeriesStore = defineStore("series", () => {
  // --- State ---
  const bundles = ref<SeriesBundle[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const lastFetchedAt = ref<number | null>(null);

  // --- Actions ---

  async function fetchSeries(args: {
    countries: string[];
    metrics: string[];
    periodFrom: string;
    periodTo: string;
  }) {
    if (!args.countries.length || !args.metrics.length) {
      error.value = "Select at least one country and one metric.";
      return;
    }
    loading.value = true;
    error.value = null;
    try {
      const qs = buildQuery(args);
      const data = await apiFetch<SeriesResponse>(`/api/series?${qs}`);
      bundles.value = data.series;
      lastFetchedAt.value = Date.now();
    } catch (e) {
      bundles.value = [];
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      loading.value = false;
    }
  }

  /** Reset chart data (e.g. after logout or when adding dashboard reset). */
  function clear() {
    bundles.value = [];
    error.value = null;
    lastFetchedAt.value = null;
  }

  return { bundles, loading, error, lastFetchedAt, fetchSeries, clear };
});
