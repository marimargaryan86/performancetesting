import type { UserModel } from "models/user";

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      user?: {
        data: UserModel;
        sessionExpiresAt: Date;
        token: string;
      };
    }
    // interface PageData {}
    // interface Platform {}
  }
}

export {};
