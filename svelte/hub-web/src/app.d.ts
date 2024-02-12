import type { Locale } from "$lib/i18n";
import type { Session, User } from "~/integration/ory/schemas/authentication";

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      user?: User;
      sessionExpiresAt?: Date;
      session: Session;
      locale: Locale;
    }
    // interface PageData {}
    // interface Platform {}
  }
}

export {};
