import type { RequestEvent } from "@sveltejs/kit";
import type { SetCookieOptions, CookieJar } from "./types";
import { getBrowserCookieJar } from "./browser";
import { getSvelteKitCookieJar } from "./server";
import { browser } from "$app/environment";

export function getCookieJar<TRequestEvent extends RequestEvent>({
  options,
  event,
}: {
  options?: SetCookieOptions;
  /** Use when running server side */
  event?: TRequestEvent;
} = {}): CookieJar {
  if (event) {
    if (browser) {
      throw new Error("Cannot use server side cookie jar in browser");
    }

    return getSvelteKitCookieJar(event, options);
  }

  if (!browser) {
    throw new Error("Cannot use client side cookie jar on server");
  }

  return getBrowserCookieJar(options);
}
