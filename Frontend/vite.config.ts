/**
 * Vite config: Vue SFC support, `@` → `src/`, and dev proxy to Flask.
 */
import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vite";
import vue from "@vitejs/plugin-vue";

export default defineConfig({
  // Compile .vue files and Vue SFC features.
  plugins: [vue()],

  // Match TypeScript `paths`: `@/components/Foo` → `src/components/Foo`.
  resolve: {
    alias: {
      "@": fileURLToPath(new URL("./src", import.meta.url)),
    },
  },

  // Dev server: same-origin `/api/*` is forwarded to Flask (cookie-friendly later).
  server: {
    port: 5173,
    proxy: {
      "/api": {
        target: "http://127.0.0.1:5000",
        changeOrigin: true,
      },
    },
  },
});
