<script setup lang="ts">
/**
 * Placeholder login route until Flask exposes `/api/auth/*` (see README Phase C).
 */

// --- Dependencies ---
import { ref } from "vue";

// --- Form model (stub: not sent to API yet) ---
const email = ref("");
const password = ref("");
const message = ref(
  "Authentication is not wired yet. When Flask exposes /api/auth/*, this form will call it with credentials: 'include'."
);

// --- Handlers ---

function onSubmit(e: Event) {
  e.preventDefault();
  message.value =
    "Stub only — no request sent. Implement register/login against your API (Phase C in the build plan).";
}
</script>

<template>
  <div class="page">
    <!-- --- Page title --- -->
    <h1>Sign in</h1>
    <p class="lede">
      Placeholder screen for the email login flow described in the README. The chart page works without auth today.
    </p>

    <!-- --- Stub form (wire to /api/auth/* later) --- -->
    <form class="card" @submit="onSubmit">
      <label class="field">
        <span>Email</span>
        <input v-model="email" type="email" autocomplete="username" placeholder="you@example.com" />
      </label>
      <label class="field">
        <span>Password</span>
        <input v-model="password" type="password" autocomplete="current-password" />
      </label>
      <button type="submit" class="primary">Sign in (stub)</button>
    </form>

    <!-- --- User-facing status text --- -->
    <p class="note">{{ message }}</p>
  </div>
</template>

<style scoped>
/* --- Page container --- */
.page {
  max-width: 420px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

h1 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.lede {
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

/* --- Form card --- */
.card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1.25rem;
  border: 1px solid var(--border);
  border-radius: 12px;
  background: var(--surface);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
  font-size: 0.85rem;
  color: var(--muted);
}

.field input {
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 1rem;
}

.primary {
  padding: 0.55rem 1rem;
  border: none;
  border-radius: 8px;
  background: var(--accent);
  color: #fff;
  font-weight: 600;
  cursor: pointer;
}

.primary:hover {
  filter: brightness(1.05);
}

/* --- Footnote message --- */
.note {
  margin-top: 1rem;
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.5;
}
</style>
