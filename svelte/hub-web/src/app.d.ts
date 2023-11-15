import type { SessionModel, UserModel } from "models/user";

// See https://kit.svelte.dev/docs/types#app
// for information about these interfaces
declare global {
  namespace App {
    // interface Error {}
    interface Locals {
      user?: UserModel;
      sessionExpiresAt?: Date;
      session: SessionModel;
    }
    // interface PageData {}
    // interface Platform {}
  }
}

export {};
