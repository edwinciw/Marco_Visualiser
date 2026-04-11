// --- Dependencies ---
import { defineStore } from "pinia";
import { ref } from "vue";
import { apiFetch } from "@/api/client";

/**
 * Lightweight connectivity check for `/api/health` (header badge).
 */
export const useHealthStore = defineStore("health", () => {
  // --- State ---
  const ok = ref<boolean | null>(null);
  const checkedAt = ref<number | null>(null);

  // --- Actions ---

  async function ping() {
    try {
      const r = await apiFetch<{ status: string }>("/api/health");
      ok.value = r.status === "ok";
    } catch {
      ok.value = false;
    } finally {
      checkedAt.value = Date.now();
    }
  }

  return { ok, checkedAt, ping };
});
