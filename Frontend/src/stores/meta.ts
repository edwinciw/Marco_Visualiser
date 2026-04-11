// --- Dependencies ---
import { defineStore } from "pinia";
import { ref, computed } from "vue";
import { apiFetch } from "@/api/client";
import type { Country, Metric } from "@/api/types";

/**
 * Reference data for filters: countries and metrics from the API, plus lookup maps for labels.
 */
export const useMetaStore = defineStore("meta", () => {
  // --- State: lists + request status ---
  const countries = ref<Country[]>([]);
  const metrics = ref<Metric[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  // --- Derived: maps for fast lookup in charts / labels ---

  // Fast lookup when rendering chart legend / tooltips by ISO3.
  const countryByIso3 = computed(() => {
    const m = new Map<string, Country>();
    for (const c of countries.value) m.set(c.iso3, c);
    return m;
  });

  // Fast lookup for metric display names and units by `metric.code`.
  const metricByCode = computed(() => {
    const m = new Map<string, Metric>();
    for (const x of metrics.value) m.set(x.code, x);
    return m;
  });

  // --- Actions ---

  /** Parallel fetch of both picklists; errors surface in `error`. */
  async function load() {
    loading.value = true;
    error.value = null;
    try {
      const [c, met] = await Promise.all([
        apiFetch<Country[]>("/api/countries"),
        apiFetch<Metric[]>("/api/metrics"),
      ]);
      countries.value = c;
      metrics.value = met;
    } catch (e) {
      error.value = e instanceof Error ? e.message : String(e);
    } finally {
      loading.value = false;
    }
  }

  return {
    countries,
    metrics,
    loading,
    error,
    countryByIso3,
    metricByCode,
    load,
  };
});
