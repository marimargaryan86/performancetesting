import { defineConfig, mergeConfig } from "vitest/config";
import sharedConfig from "@snowfall/vitest-config";

export default defineConfig((configEnv) =>
  mergeConfig(
    sharedConfig(configEnv),
    defineConfig({
      // Add package specific test config here
    }),
  ),
);
