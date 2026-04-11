<script setup lang="ts">
/**
 * Top bar: app title, primary nav links, and API health indicator from `/api/health`.
 */

// --- Dependencies ---
import { RouterLink } from "vue-router";
import { onMounted } from "vue";
import { storeToRefs } from "pinia";
import { useHealthStore } from "@/stores/health";

// --- Health store (API dot in header) ---
const health = useHealthStore();
const { ok } = storeToRefs(health);

// --- Lifecycle ---
onMounted(() => {
  health.ping();
});
</script>

<template>
  <!-- --- Header bar --- -->
  <header class="header">
    <!-- Product identity + link home. -->
    <div class="brand">
      <RouterLink to="/" class="logo">Macro vis</RouterLink>
      <span class="tagline">Time series explorer</span>
    </div>
    <!-- Main routes: charts (default) and login stub. -->
    <nav class="nav">
      <RouterLink to="/" class="nav-link">Charts</RouterLink>
      <RouterLink to="/login" class="nav-link">Login</RouterLink>
    </nav>
    <!-- Traffic-light style dot: null=pending, true=ok, false=down. -->
    <div class="status" :title="ok === null ? 'Checking API…' : ok ? 'API reachable' : 'API unreachable'">
      <span class="dot" :class="{ ok: ok === true, bad: ok === false, pending: ok === null }" />
      <span class="label">API</span>
    </div>
  </header>
</template>

<style scoped>
/* --- Header layout --- */
.header {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid var(--border);
  background: var(--surface);
}

/* --- Brand / title --- */
.brand {
  display: flex;
  flex-direction: column;
  gap: 0.1rem;
}

.logo {
  font-weight: 700;
  font-size: 1.15rem;
  letter-spacing: -0.02em;
  color: var(--text);
  text-decoration: none;
}

.logo:hover {
  color: var(--accent);
}

.tagline {
  font-size: 0.75rem;
  color: var(--muted);
}

/* --- Primary navigation --- */
.nav {
  display: flex;
  gap: 0.5rem;
  margin-left: auto;
}

.nav-link {
  padding: 0.4rem 0.75rem;
  border-radius: 8px;
  font-size: 0.9rem;
  color: var(--muted);
  text-decoration: none;
}

.nav-link:hover {
  color: var(--text);
  background: var(--surface-2);
}

.nav-link.router-link-active {
  color: var(--accent);
  background: rgba(37, 99, 235, 0.08);
}

/* --- API status indicator --- */
.status {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8rem;
  color: var(--muted);
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #94a3b8;
}

.dot.ok {
  background: #16a34a;
}

.dot.bad {
  background: #dc2626;
}

.dot.pending {
  animation: pulse 1s ease-in-out infinite;
}

@keyframes pulse {
  50% {
    opacity: 0.45;
  }
}
</style>
