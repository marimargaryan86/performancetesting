import { describe, it, expect, vi } from "vitest";
import { getBrowserCookieJar } from "../browser";

function spy(): void {
  let cookies = "";

  vi.spyOn(document, "cookie", "get").mockImplementation(() => {
    return cookies;
  });

  vi.spyOn(document, "cookie", "set").mockImplementation((value: string) => {
    const cookie = value.split("; ")[0];

    if (cookie?.endsWith("=")) {
      const name = cookie.split("=")[0];

      cookies = cookies
        .split("; ")
        .filter((item) => !item.startsWith(`${name}=`))
        .join("; ");
    } else {
      cookies = [...cookies.split("; ").filter((item) => item !== ""), cookie].join("; ");
    }
  });
}

describe("getBrowserCookieJar", () => {
  it("should get a browser cookie jar", () => {
    spy();
    const cookieJar = getBrowserCookieJar({});

    expect(cookieJar.get("foo")).toBeUndefined();
    expect(cookieJar.set("foo", "bar")).toBeUndefined();
    expect(cookieJar.get("foo")).toBe("bar");
    expect(cookieJar.set("bar", "baz", { secure: true })).toBeUndefined();
    expect(cookieJar.get("bar", {})).toBeUndefined();
    expect(cookieJar.get("bar", { secure: true })).toBe("baz");
    expect(cookieJar.set("bar", "foo")).toBeUndefined();
    expect(cookieJar.get("bar", { secure: true })).toBe("baz");
    expect(cookieJar.get("bar")).toBe("foo");
    expect(cookieJar.delete("bar")).toBeUndefined();
    expect(cookieJar.get("bar")).toBeUndefined();
    expect(cookieJar.get("bar", { secure: true })).toBe("baz");
    expect(cookieJar.delete("bar", { secure: true })).toBeUndefined();
    expect(cookieJar.get("bar", { secure: true })).toBeUndefined();
  });
});
