import { describe, expect, it, vi } from "vitest";
import { getClient, type ClientMethods } from "..";
import type { ServerResponseData } from "$lib/rpc-base/server";

class CustomError extends Error {
  //
}

type RouteId = "/foo/bar";
type ServerMapping = { get: (b: string, a: number) => boolean; find: () => string };
type ClientMapping = { get: (a: number, b: string) => [a: string, b: number] };
type ErrorMapping = { type: "Error"; args: [string] } | { type: "CustomError"; args: [string] };

const fetchMock = vi.fn();
global.fetch = fetchMock;

function createClient(): ClientMethods<ServerMapping, ClientMapping> {
  return getClient<RouteId, ServerMapping, ClientMapping, ErrorMapping>(
    "/foo/bar",
    {
      get: (a: number, b: string): [a: string, b: number] => [b, a],
    },
    {
      requestParser: JSON,
      responseParser: JSON,
      errorParser: {
        serialize(error) {
          if (error instanceof CustomError) {
            return {
              type: "CustomError",
              args: [`Custom: ${error.message}`],
            } as const;
          }

          return {
            type: "Error",
            args: [error.message],
          } as const;
        },
        deserialize(data) {
          return new Error(...data.args);
        },
      },
    },
  );
}

describe("getClient", () => {
  it("should get a client", () => {
    const client = createClient();

    expect(client).toHaveProperty("get");
    expect(client).not.toHaveProperty("find");
  });

  it("should call a client with successful responses", async () => {
    const client = createClient();

    fetchMock.mockImplementation(
      (_: URL, options: { body: string }) =>
        new Promise((resolve) =>
          resolve({
            text: () =>
              new Promise((resolveText) =>
                resolveText(
                  JSON.stringify({
                    success: true,
                    data: JSON.parse(options.body)[1] === 23,
                  } satisfies ServerResponseData),
                ),
              ),
          }),
        ),
    );

    await expect(client.get(23, "foo")).resolves.toBe(true);
    await expect(client.get(24, "foo")).resolves.toBe(false);
  });

  it("should call a client with an error", async () => {
    const client = createClient();

    fetchMock.mockImplementation(
      (url: URL, options: { body: string }) =>
        new Promise((resolve) =>
          resolve({
            text: () =>
              new Promise((resolveText) =>
                resolveText(
                  JSON.stringify({
                    success: false,
                    error: {
                      type: "Error",
                      args: [JSON.parse(options.body)[0]],
                    },
                  } satisfies ServerResponseData),
                ),
              ),
          }),
        ),
    );

    await expect(client.get(23, "foo")).rejects.toThrowError("foo");
    await expect(client.get(23, "foo")).rejects.not.toThrowError("bar");
  });
});
