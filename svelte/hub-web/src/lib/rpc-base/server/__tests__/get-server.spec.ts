import { describe, expect, it } from "vitest";
import { getServer, type ServerEndpoint } from "..";
import type { MaybePromise, RequestEvent } from "@sveltejs/kit";

function createServer(): ServerEndpoint<RequestEvent> {
  return getServer({
    requestParser: JSON,
    responseParser: JSON,
    errorParser: {
      serialize(error) {
        return {
          type: "Error",
          args: [error.message],
        } as const;
      },
      deserialize(data) {
        return new Error(...data.args);
      },
    },
  })({
    get: (a: number, b: string) => a === 23 || b === "foo",
  });
}

describe("getServer", () => {
  it("should create a server", async () => {
    const server = createServer();

    function callServer(a: number, b: string): MaybePromise<Response> {
      return server({
        url: new URL("http://localhost/foo/bar?action=get"),
        request: { text: () => new Promise((resolve) => resolve(JSON.stringify([a, b]))) },
      } as RequestEvent);
    }

    await expect(callServer(23, "bar")).resolves.toBeInstanceOf(Response);
  });
});
