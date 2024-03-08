// See https://kit.svelte.dev/docs/types#app

import type { Locale } from "$lib/i18n/lang";

// for information about these interfaces
declare global {
  declare module "svelte-icons/fa/*.svelte" {
    import { SvelteComponentTyped } from "svelte";
    export default class extends SvelteComponentTyped<> {}
  }
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
