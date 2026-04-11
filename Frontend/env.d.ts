/// <reference types="vite/client" />

// Vite injects string env vars at build time; declare them for TypeScript.

interface ImportMetaEnv {
  /** API origin (optional). Empty = relative URLs, often combined with Vite proxy in dev. */
  readonly VITE_API_BASE_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
