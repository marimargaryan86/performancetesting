// See https://kit.svelte.dev/docs/types#app

import type { Locale } from "$lib/i18n/lang";

// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      locale: Locale;
    }
    // interface PageData {}
    // interface PageState {}
    // interface Platform {}
  }
}

export {};
