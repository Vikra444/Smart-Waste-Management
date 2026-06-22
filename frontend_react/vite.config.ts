import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { tanstackStart } from "@tanstack/react-start/plugin/vite";
import tailwindcss from "@tailwindcss/vite";
import { cloudflare } from "@cloudflare/vite-plugin";

export default defineConfig({
  plugins: [
    tanstackStart({
      server: { entry: "server" },
    }),
    react(),
    tailwindcss(),
    tsconfigPaths(),
    process.env.NODE_ENV === "production" && cloudflare(),
  ].filter(Boolean),
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ""),
      },
      "/telemetry": { target: "http://localhost:8000", changeOrigin: true },
      "/route":     { target: "http://localhost:8000", changeOrigin: true },
      "/health":    { target: "http://localhost:8000", changeOrigin: true },
      "/bins":      { target: "http://localhost:8000", changeOrigin: true },
      "/complaints":{ target: "http://localhost:8000", changeOrigin: true },
      "/predict":   { target: "http://localhost:8000", changeOrigin: true },
      "/iot":       { target: "http://localhost:8000", changeOrigin: true },
    },
  },
});
