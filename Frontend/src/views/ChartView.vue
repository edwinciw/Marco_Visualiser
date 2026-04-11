<script setup lang="ts">
/**
 * Main dashboard page: load countries/metrics, pick filters, fetch `/api/series`, render chart.
 */

// --- Dependencies ---
import { onMounted, ref, watch } from "vue";
import { storeToRefs } from "pinia";
import { useMetaStore } from "@/stores/meta";
import { useSeriesStore } from "@/stores/series";
import TimeSeriesChart from "@/components/TimeSeriesChart.vue";

// --- Pinia (reactive picks from stores) ---
const meta = useMetaStore();
const series = useSeriesStore();
const { countries, metrics, loading: metaLoading, error: metaError } = storeToRefs(meta);
const { bundles, loading: seriesLoading, error: seriesError } = storeToRefs(series);

// --- Local filter state (bound to template) ---
const selectedCountries = ref<string[]>([]);
const selectedMetrics = ref<string[]>([]);
const periodFrom = ref("");
const periodTo = ref("");

// --- Filter helpers ---

/** Add/remove item in a multi-select list (mutates array in place for checkbox binding). */
function toggle<T>(arr: T[], item: T) {
  const i = arr.indexOf(item);
  if (i >= 0) arr.splice(i, 1);
  else arr.push(item);
}

/** Sensible first load: up to 3 countries + first metric so the chart isn’t empty. */
function applyDefaults() {
  if (!countries.value.length || !metrics.value.length) return;
  if (!selectedCountries.value.length) {
    const n = Math.min(3, countries.value.length);
    selectedCountries.value = countries.value.slice(0, n).map((c) => c.iso3);
  }
  if (!selectedMetrics.value.length) {
    selectedMetrics.value = [metrics.value[0].code];
  }
}

// --- Load series into store ---

async function loadChart() {
  await series.fetchSeries({
    countries: selectedCountries.value,
    metrics: selectedMetrics.value,
    periodFrom: periodFrom.value,
    periodTo: periodTo.value,
  });
}

// --- Initial load + keep defaults in sync when meta lists arrive ---

onMounted(async () => {
  await meta.load();
  applyDefaults();
  await loadChart();
});

watch(
  () => [countries.value.length, metrics.value.length] as const,
  () => {
    applyDefaults();
  }
);
</script>

<template>
  <div class="page">
    <!-- --- Intro copy --- -->
    <section class="intro">
      <h1>Macroeconomic time series</h1>
      <p class="lede">
        Choose countries and metrics, optionally bound the period (lexicographic:
        <code>YYYY</code> or <code>YYYY-Qn</code>), then load the chart. Data comes from your Flask
        <code>/api/series</code> endpoint.
      </p>
    </section>

    <!-- --- API error banners --- -->
    <div v-if="metaError" class="banner error">{{ metaError }}</div>
    <div v-if="seriesError" class="banner error">{{ seriesError }}</div>

    <div class="layout">
      <!-- --- Sidebar: filters --- -->
      <aside class="panel filters" :aria-busy="metaLoading">
        <h2>Filters</h2>
        <p v-if="metaLoading" class="hint">Loading reference data…</p>

        <div class="block">
          <h3>Countries</h3>
          <ul class="checklist">
            <li v-for="c in countries" :key="c.id">
              <label class="check">
                <input
                  type="checkbox"
                  :checked="selectedCountries.includes(c.iso3)"
                  @change="toggle(selectedCountries, c.iso3)"
                />
                <span>{{ c.name }}</span>
                <span class="iso">{{ c.iso3 }}</span>
              </label>
            </li>
          </ul>
        </div>

        <div class="block">
          <h3>Metrics</h3>
          <ul class="checklist">
            <li v-for="m in metrics" :key="m.id">
              <label class="check">
                <input
                  type="checkbox"
                  :checked="selectedMetrics.includes(m.code)"
                  @change="toggle(selectedMetrics, m.code)"
                />
                <span>{{ m.name }}</span>
                <span class="iso">{{ m.code }}</span>
              </label>
            </li>
          </ul>
        </div>

        <div class="block row">
          <label class="field">
            <span>Period from</span>
            <input v-model="periodFrom" type="text" placeholder="e.g. 2000" autocomplete="off" />
          </label>
          <label class="field">
            <span>Period to</span>
            <input v-model="periodTo" type="text" placeholder="e.g. 2024" autocomplete="off" />
          </label>
        </div>

        <button type="button" class="primary" :disabled="seriesLoading || metaLoading" @click="loadChart">
          {{ seriesLoading ? "Loading…" : "Load chart" }}
        </button>
      </aside>

      <!-- --- Main: chart --- -->
      <main class="panel chart-panel">
        <h2>Chart</h2>
        <TimeSeriesChart :bundles="bundles" :metric-lookup="meta.metricByCode" />
        <p v-if="!seriesLoading && !bundles.length && !seriesError" class="hint empty">
          No series returned. Pick countries and metrics that exist in the database, then load again.
        </p>
      </main>
    </div>
  </div>
</template>

<style scoped>
/* --- Page shell --- */
.page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 1.5rem;
}

/* --- Intro typography --- */
.intro h1 {
  font-size: 1.65rem;
  font-weight: 700;
  letter-spacing: -0.03em;
  margin-bottom: 0.5rem;
}

.lede {
  color: var(--muted);
  font-size: 0.95rem;
  line-height: 1.55;
  max-width: 52rem;
}

.lede code {
  font-size: 0.85em;
  padding: 0.1em 0.35em;
  border-radius: 4px;
  background: var(--surface-2);
}

/* --- Error banners --- */
.banner {
  margin: 1rem 0;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  font-size: 0.9rem;
}

.banner.error {
  background: #fef2f2;
  color: #991b1b;
  border: 1px solid #fecaca;
}

/* --- Two-column layout (filters | chart) --- */
.layout {
  display: grid;
  grid-template-columns: minmax(240px, 300px) 1fr;
  gap: 1.25rem;
  margin-top: 1.25rem;
}

@media (max-width: 880px) {
  .layout {
    grid-template-columns: 1fr;
  }
}

/* --- Card panels --- */
.panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 1.1rem 1.15rem;
}

.panel h2 {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.filters h3 {
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--muted);
  margin-bottom: 0.45rem;
}

.block {
  margin-bottom: 1rem;
}

.block.row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.65rem;
}

/* --- Checkbox lists --- */
.checklist {
  list-style: none;
  max-height: 200px;
  overflow: auto;
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 0.35rem 0;
}

.check {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.35rem 0.65rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.check:hover {
  background: var(--surface-2);
}

.check input {
  flex-shrink: 0;
}

.iso {
  margin-left: auto;
  font-size: 0.75rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

/* --- Period inputs --- */
.field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  font-size: 0.8rem;
  color: var(--muted);
}

.field input {
  padding: 0.45rem 0.55rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 0.9rem;
}

/* --- Primary action --- */
.primary {
  width: 100%;
  margin-top: 0.25rem;
  padding: 0.55rem 1rem;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
}

.primary:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.primary:not(:disabled):hover {
  filter: brightness(1.05);
}

/* --- Hints / empty state --- */
.hint {
  font-size: 0.85rem;
  color: var(--muted);
  margin-bottom: 0.75rem;
}

.hint.empty {
  margin-top: 0.75rem;
}

.chart-panel h2 {
  margin-bottom: 0.35rem;
}
</style>
