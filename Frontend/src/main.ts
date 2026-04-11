/**
 * Application bootstrap: Vue root, global state (Pinia), routing, base styles.
 */

// --- Dependencies ---
import { createApp } from "vue";
import { createPinia } from "pinia";
import App from "./App.vue";
import { router } from "./router";
import "./assets/main.css";

// --- Create app & global plugins ---
const app = createApp(App);

// Pinia stores (meta, series, health) are created on demand via useXStore().
app.use(createPinia());

// Client-side routes: / charts, /login stub.
app.use(router);

// --- Mount ---
app.mount("#app");
