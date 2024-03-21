/* eslint-disable no-console */
import dotenv from "dotenv";
import path from "path";
import { fileURLToPath } from "url";

export const setupEnvironment = (): void => {
  const __dirname = path.dirname(fileURLToPath(import.meta.url));
  dotenv.config({ path: path.join(__dirname, "../../.env") });
};

export const checkEnvironmentVariables = (): void => {
  if (!process.env.E2E_USERNAME || !process.env.E2E_PASSWORD) {
    console.error(
      "ERROR: E2E_USERNAME and E2E_PASSWORD environment variables are not properly set. Please set them in your .env file.",
    );
    throw new Error("Missing E2E_USERNAME or E2E_PASSWORD environment variables");
  }
};
