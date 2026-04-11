<script setup lang="ts">
// --- Shell layout: persistent header + outlet for the active route ---
import { RouterView } from "vue-router";
import AppHeader from "@/components/AppHeader.vue";
</script>

<template>
  <!-- --- App shell --- -->
  <div class="app">
    <AppHeader />
    <RouterView />
  </div>
</template>

<style scoped>
/* --- Root layout column (header + page content) --- */
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg);
}
</style>
