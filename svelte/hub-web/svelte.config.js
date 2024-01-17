import { preprocessMeltUI, sequence } from "@melt-ui/pp";
import adapter from "@sveltejs/adapter-node";
import { vitePreprocess } from "@sveltejs/kit/vite";

/** @type {import('@sveltejs/kit').Config}*/
const config = {
  // Consult https://kit.svelte.dev/docs/integrations#preprocessors
  // for more information about preprocessors
  preprocess: sequence([vitePreprocess(), preprocessMeltUI()]),
  vitePlugin: {
    inspector: {
      toggleKeyCombo: "control-shift",
    },
  },
  kit: {
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
