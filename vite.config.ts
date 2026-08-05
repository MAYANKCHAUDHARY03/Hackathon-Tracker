import path from "path"
import { defineConfig } from "vite"
import react from "@vitejs/plugin-react"

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": path.resolve(import.meta.dirname, "./src"),
    },
  },
  server: {
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
      },
    },
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id: string) {
          if (id.includes("node_modules")) {
            if (id.includes("react-dom") || id.includes("react-router-dom")) {
              return "vendor"
            }
            if (
              id.includes("lucide-react") ||
              id.includes("framer-motion") ||
              id.includes("recharts") ||
              id.includes("@tanstack/react-table")
            ) {
              return "ui"
            }
          }
        },
      },
    },
  },
})
