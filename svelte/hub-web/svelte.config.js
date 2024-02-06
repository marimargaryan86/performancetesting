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
      "~/integration-instances-client": "src/integration-instances.client.ts",
      "~/integration-instances": "src/integration-instances.server.ts",
      "~": "src",
    },
  },
};
export default config;
