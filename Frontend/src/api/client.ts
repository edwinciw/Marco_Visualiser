// --- Types ---
import type { ApiErrorBody } from "./types";

// --- Base URL from env (empty = same-origin / Vite proxy) ---

/**
 * Resolve optional absolute API origin from env; empty means relative paths (proxy-friendly).
 */
function apiOrigin(): string {
  const base = import.meta.env.VITE_API_BASE_URL?.trim() ?? "";
  return base.replace(/\/$/, "");
}

/** Build full URL: either `https://api.example.com/api/...` or `/api/...`. */
export function apiUrl(path: string): string {
  const origin = apiOrigin();
  if (!origin) return path;
  return `${origin}${path.startsWith("/") ? path : `/${path}`}`;
}

// --- HTTP client ---

/**
 * Typed fetch wrapper: sends cookies (session/JWT later), parses JSON, throws on HTTP errors.
 */
export async function apiFetch<T>(
  path: string,
  init?: RequestInit
): Promise<T> {
  const url = apiUrl(path);
  const res = await fetch(url, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...init?.headers,
    },
  });

  const text = await res.text();
  let body: unknown = null;
  if (text) {
    try {
      body = JSON.parse(text) as unknown;
    } catch {
      body = { error: text };
    }
  }

  if (!res.ok) {
    const err = (body as ApiErrorBody)?.error ?? res.statusText;
    throw new Error(typeof err === "string" ? err : `HTTP ${res.status}`);
  }

  return body as T;
}
