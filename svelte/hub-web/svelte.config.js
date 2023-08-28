import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/kit/vite";

/** @type {import('@sveltejs/kit').Config} */
const config = {
  // Consult https://kit.svelte.dev/docs/integrations#preprocessors
  // for more information about preprocessors
  preprocess: vitePreprocess(),

  kit: {
    adapter: adapter(),
    alias: {
      components: "src/components",
      assets: "src/assets",
      integration: "src/integration",
      "integration-instances": "src/integration-instances.server.ts",
      models: "src/models",
      config: "src/config",
      utils: "src/utils",
      formatting: "src/formatting",
      directives: "src/directives",
      filters: "src/filters",
      sorting: "src/sorting",
      transitions: "src/transitions",
      routeConfig: "src/route-config.ts",
    },
  },
};

export default config;
