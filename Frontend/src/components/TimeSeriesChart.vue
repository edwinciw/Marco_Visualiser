<script setup lang="ts">
/**
 * ECharts line chart: one line per (country × metric) bundle from `/api/series`.
 * Aligns all series on a shared, sorted period axis (gaps become nulls).
 */

// --- Dependencies ---
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import * as echarts from "echarts";
import type { Metric, SeriesBundle } from "@/api/types";

// --- Props ---
const props = defineProps<{
  bundles: SeriesBundle[];
  metricLookup: Map<string, Metric>;
}>();

// --- Chart instance (non-reactive: ECharts owns its DOM) ---
const host = ref<HTMLDivElement | null>(null);
let chart: echarts.ECharts | null = null;

// --- Data shaping for ECharts ---

/** Union of all periods across bundles, sorted lexicographically (matches API convention). */
function sortedPeriods(bundles: SeriesBundle[]): string[] {
  const set = new Set<string>();
  for (const b of bundles) {
    for (const p of b.points) set.add(p.period);
  }
  return [...set].sort();
}

/** Full ECharts option: empty state title vs multi-series line chart. */
const option = computed(() => {
  const categories = sortedPeriods(props.bundles);
  if (!categories.length) {
    return {
      title: {
        text: "No observations in range",
        left: "center",
        top: "middle",
        textStyle: { color: "#64748b", fontSize: 15, fontWeight: 400 },
      },
    };
  }

  const series = props.bundles.map((b) => {
    const map = new Map(b.points.map((p) => [p.period, p.value]));
    const data = categories.map((period) => map.get(period) ?? null);
    const m = props.metricLookup.get(b.metric_code);
    const unit = m?.unit ? ` (${m.unit})` : "";
    const name = `${b.country_iso3} · ${m?.name ?? b.metric_code}${unit}`;
    return {
      name,
      type: "line" as const,
      smooth: true,
      symbol: "circle",
      symbolSize: 6,
      showSymbol: categories.length <= 24,
      connectNulls: false,
      data,
    };
  });

  return {
    color: [
      "#2563eb",
      "#059669",
      "#d97706",
      "#7c3aed",
      "#db2777",
      "#0d9488",
      "#b45309",
      "#4f46e5",
    ],
    grid: { left: 56, right: 24, top: 48, bottom: 72 },
    tooltip: {
      trigger: "axis",
      axisPointer: { type: "cross" },
    },
    legend: {
      type: "scroll",
      bottom: 0,
      textStyle: { color: "#475569" },
    },
    xAxis: {
      type: "category",
      data: categories,
      boundaryGap: false,
      axisLabel: { color: "#64748b", rotate: categories.some((p) => p.length > 4) ? 35 : 0 },
    },
    yAxis: {
      type: "value",
      scale: true,
      splitLine: { lineStyle: { color: "#e2e8f0" } },
      axisLabel: { color: "#64748b" },
    },
    series,
  };
});

// --- Window resize ---

function resize() {
  chart?.resize();
}

// --- Lifecycle: init / sync option / teardown ---

onMounted(() => {
  if (!host.value) return;
  chart = echarts.init(host.value, undefined, { renderer: "canvas" });
  chart.setOption(option.value, true);
  window.addEventListener("resize", resize);
});

watch(
  () => option.value,
  (opt) => {
    chart?.setOption(opt, true);
  },
  { deep: true }
);

onBeforeUnmount(() => {
  window.removeEventListener("resize", resize);
  chart?.dispose();
  chart = null;
});
</script>

<template>
  <!-- ECharts mount target (canvas size follows this div). -->
  <div ref="host" class="chart-host" />
</template>

<style scoped>
/* --- Chart container sizing --- */
.chart-host {
  width: 100%;
  min-height: 420px;
  height: min(58vh, 640px);
}
</style>
