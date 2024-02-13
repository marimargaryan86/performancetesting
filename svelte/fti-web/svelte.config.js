import { preprocessMeltUI, sequence } from "@melt-ui/pp";
import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/vite-plugin-svelte";
/** @type {import('@sveltejs/kit').Config}*/
const config = {
  // Consult https://kit.svelte.dev/docs/integrations#preprocessors
  // for more information about preprocessors
  preprocess: sequence([vitePreprocess(), preprocessMeltUI()]),
  kit: {
    // adapter-auto only supports some environments, see https://kit.svelte.dev/docs/adapter-auto for a list.
    // If your environment is not supported or you settled on a specific environment, switch out the adapter.
    // See https://kit.svelte.dev/docs/adapters for more information about adapters.
    adapter: adapter(),
    alias: {
      components: "src/components",
      assets: "src/assets",
      data: "src/data",
      directives: "src/directives",
      filters: "src/filters",
      formatting: "src/formatting",
      i18n: "src/i18n",
      integration: "src/integration",
      models: "src/models",
      sorting: "src/sorting",
      stores: "src/stores",
      transitions: "src/transitions",
      utils: "src/utils",
      "integration-instances-client": "src/integration-instances.client.ts",
      "integration-instances": "src/integration-instances.server.ts",
      routeConfig: "src/route-config.ts",
    },
  },
};
export default config;
