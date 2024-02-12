import type { Locale } from "$lib/i18n";
import type * as OrySchemas from "~/integration/ory/schemas";

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      user?: OrySchemas.User;
      sessionExpiresAt?: Date;
      session: OrySchemas.Session;
      locale: Locale;
    }
    // interface PageData {}
    // interface Platform {}
  }
}

export {};
