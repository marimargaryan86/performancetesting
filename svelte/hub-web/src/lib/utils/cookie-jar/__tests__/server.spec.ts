import { describe, it, expect } from "vitest";
import { getSvelteKitCookieJar } from "../server";
import type { RequestEvent } from "@sveltejs/kit";

function getRequestEvent(): RequestEvent {
  const cookies: Record<string, string> = {};

  return {
    cookies: {
      get(name: string) {
        return cookies[name];
      },
      set(name: string, value: string) {
        cookies[name] = value;
      },
      delete(name: string) {
        delete cookies[name];
      },
    },
  } as unknown as RequestEvent;
}

describe("getSvelteKitCookieJar", () => {
  it("Should get a svelte kit cookie jar", () => {
    const cookieJar = getSvelteKitCookieJar(getRequestEvent(), {});

    expect(cookieJar.get("foo")).toBeUndefined();
    expect(cookieJar.set("foo", "bar")).toBeUndefined();
    expect(cookieJar.get("foo")).toBe("bar");
    expect(cookieJar.get("foo", { secure: true })).toBeUndefined();
    expect(cookieJar.set("foo", "baz", { secure: true })).toBeUndefined();
    expect(cookieJar.get("foo", { secure: true })).toBe("baz");
    expect(cookieJar.delete("foo")).toBeUndefined();
    expect(cookieJar.get("foo")).toBeUndefined();
    expect(cookieJar.get("foo", { secure: true })).toBe("baz");
    expect(cookieJar.delete("foo", { secure: true })).toBeUndefined();
    expect(cookieJar.get("foo", { secure: true })).toBeUndefined();
  });
});
