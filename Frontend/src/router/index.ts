/**
 * Vue Router table: maps paths to page components (lazy loading optional later).
 */

// --- Route components ---
import { createRouter, createWebHistory } from "vue-router";
import ChartView from "@/views/ChartView.vue";
import LoginView from "@/views/LoginView.vue";

// --- Router instance ---
export const router = createRouter({
  // Uses Vite BASE_URL when the app is deployed under a subpath.
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: "/", name: "charts", component: ChartView },
    { path: "/login", name: "login", component: LoginView },
  ],
});
