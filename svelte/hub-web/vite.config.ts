// import { sentrySvelteKit } from "@sentry/sveltekit";
import { defineConfig, type UserConfigExport } from "vite";
import { sveltekit } from "@sveltejs/kit/vite";

export default defineConfig(({ command }) => {
  const config: UserConfigExport = {
    plugins: [
      // sentrySvelteKit(),
      sveltekit(),
    ],
  };

  if (command === "build") {
    // Set a temporary JWT_SECRET to pass the build
    process.env.JWT_SECRET = new Date().toISOString();
  }

  return config;
});
