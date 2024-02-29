/// <reference types="vitest" />
import path from "path";
import { defineConfig } from "vitest/config";
import { sveltekit } from "@sveltejs/kit/vite";

/** @type {import("vitest/config").UserConfig} */
export default defineConfig(({ mode }) => ({
  plugins: [
    // sentrySvelteKit(),
    sveltekit(),
  ],
  resolve: {
    conditions: mode === "test" ? ["browser"] : [],
  },
  test: {
    environment: "happy-dom",
    include: ["src/**/*.{test,spec}.{js,ts}"],
    setupFiles: ["./vitest-setup.js"],
  },
}));
