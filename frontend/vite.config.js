// Vite config: React + Tailwind CSS v4, "@" path alias, and a dev proxy so
// requests to /api are forwarded to the FastAPI backend on port 8000.
import path from "node:path";
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";

export default defineConfig({
  plugins: [react(), tailwindcss()],
  resolve: { alias: { "@": path.resolve(import.meta.dirname, "src") } },
  build: { chunkSizeWarningLimit: 700 },
  server: {
    port: 5173,
    // Allow temporary public tunnel links (localhost.run) to reach the dev server
    allowedHosts: [".lhr.life", ".localhost.run"],
    proxy: { "/api": { target: "http://127.0.0.1:8000", changeOrigin: true } },
  },
});
