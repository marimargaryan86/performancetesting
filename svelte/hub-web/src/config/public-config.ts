import { env } from "$env/dynamic/public";

function validateExists(key: keyof typeof env): string {
  const value = env[key];

  if (value === undefined) {
    throw new Error(`Missing env variable ${key}`);
  }

  return value;
}

const config: typeof env = {
  PUBLIC_PAY_ADMIN_API_BASE_URL: validateExists("PUBLIC_PAY_ADMIN_API_BASE_URL"),
  PUBLIC_PAY_API_BASE_URL: validateExists("PUBLIC_PAY_API_BASE_URL"),
};

export default config;
