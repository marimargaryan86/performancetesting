/** @type {import('@playwright/test').PlaywrightTestConfig} */
const config = {
  webServer: {
    command: "yarn run build && yarn run preview",
    port: 3000,
  },
};

export default config;
