import { defineConfig } from "@hey-api/openapi-ts";

export default defineConfig({
  input: [
    "http://localhost:8001/openapi.json", // Auth Service
    "http://localhost:8000/openapi.json", // Users Service
    "http://localhost:8004/openapi.json", // Contracts Service
  ],
  output: "src/api/generated",
  plugins: ["@tanstack/react-query"],
});
