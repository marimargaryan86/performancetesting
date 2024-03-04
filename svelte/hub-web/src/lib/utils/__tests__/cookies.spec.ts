import { describe, it, expect } from "vitest";
import { getCookiesFromHeaders } from "../cookies";

describe("getCookiesFromHeaders", () => {
  it("should return an empty array if cookie header is not present", () => {
    const headers = new Headers();
    const cookies = getCookiesFromHeaders(headers);
    expect(cookies).toEqual([]);
  });

  it("should parse cookie header correctly", () => {
    const headers = new Headers();
    headers.set("set-cookie", "name=value; Path=/; Domain=example.com");

    const cookies = getCookiesFromHeaders(headers);

    expect(cookies).toEqual([
      {
        name: "name",
        value: "value",
        path: "/",
        domain: "example.com",
        maxAge: undefined,
        httpOnly: false,
        secure: false,
        expires: undefined,
        sameSite: undefined,
        priority: undefined,
      },
    ]);
  });

  it("should handle multiple cookies in the header", () => {
    const headers = new Headers();
    headers.set(
      "set-cookie",
      "name1=value1; Path=/; Domain=example.com, name2=value2; Path=/; Domain=example.com",
    );

    const cookies = getCookiesFromHeaders(headers);

    expect(cookies).toEqual([
      {
        name: "name1",
        value: "value1",
        path: "/",
        domain: "example.com",
        maxAge: undefined,
        httpOnly: false,
        secure: false,
        expires: undefined,
        sameSite: undefined,
        priority: undefined,
      },
      {
        name: "name2",
        value: "value2",
        path: "/",
        domain: "example.com",
        maxAge: undefined,
        httpOnly: false,
        secure: false,
        expires: undefined,
        sameSite: undefined,
        priority: undefined,
      },
    ]);
  });
});
