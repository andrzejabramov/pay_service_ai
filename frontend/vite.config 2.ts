import path from "path";
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
  server: {
    proxy: {
      // Auth Service (порт 8001)
      "/api/v1/auth": {
        target: "http://localhost:8001",
        changeOrigin: true,
      },
      // Users Service (порт 8000)
      "/accounts": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
      // Contracts Service (порт 8004)
      "/tariffs": {
        target: "http://localhost:8004",
        changeOrigin: true,
      },
      "/organisations": {
        target: "http://localhost:8004",
        changeOrigin: true,
      },
      "/services": {
        target: "http://localhost:8004",
        changeOrigin: true,
      },
      "/communications": {
        target: "http://localhost:8004",
        changeOrigin: true,
      },
      "/payments": {
        target: "http://localhost:8004",
        changeOrigin: true,
      },
    },
  },
});
