/* eslint-disable class-methods-use-this, @typescript-eslint/no-unused-vars */
import { describe, expect, it, vi } from "vitest";
import { createRPCBase } from "../..";
import type { RequestEvent } from "@sveltejs/kit";

type MyRequestEvent = RequestEvent<Record<string, string>, "/foo/bar/baz">;

class MyService {
  get(foo: string): Promise<number> {
    throw new Error("Not implemented");
  }

  find(bar: number, baz: boolean): Promise<number> {
    throw new Error("Not implemented");
  }

  del(): void {
    throw new Error("Not implemented");
  }
}

class CustomError extends Error {
  //
}

const fetchMock = vi.fn();
global.fetch = fetchMock;

describe("createRPCBase", () => {
  it("should create a RPC base", () => {
    const rpcBase = createRPCBase();

    expect(typeof rpcBase).toBe("function");
  });

  it("should create a RPC base factory", () => {
    const rpcBase = createRPCBase();
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");

    expect(typeof factory).toBe("function");
  });

  it("should create a client and a server function", () => {
    const rpcBase = createRPCBase();
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");
    const { client, server } = factory({ get: (a: number) => [a] as const });

    expect(typeof server).toBe("function");
    expect(client).toHaveProperty("get");
  });

  it("should create a server", () => {
    const rpcBase = createRPCBase();
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");
    const { server } = factory({ get: (a: number) => [a] as const });
    const POST = server({ get: (event, a) => new Promise((resolve) => resolve(a)) });

    expect(typeof POST).toBe("function");
  });

  it("should call the client", async () => {
    const rpcBase = createRPCBase();
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");
    const { client } = factory({ get: (a: number) => [a] as const });
    fetchMock.mockResolvedValue({
      text: () => new Promise((resolve) => resolve(JSON.stringify({ success: true, data: 123 }))),
    });

    await expect(client.get(123)).resolves.toEqual(123);
  });

  it("should call the server", async () => {
    const rpcBase = createRPCBase();
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");
    const { server } = factory({ get: (a: number) => [a] as const });
    const POST = server({ get: (event, a) => new Promise((resolve) => resolve(a)) });

    await expect(
      POST({
        url: new URL("http://localhost/foo/bar/baz?action=get"),
        request: { text: () => new Promise((resolve) => resolve("[123]")) },
      } as MyRequestEvent),
    ).resolves.toBeInstanceOf(Response);
  });

  it("should call the server from the client and get a response", async () => {
    const rpcBase = createRPCBase();
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");
    const { client, server } = factory({ get: (a: number) => [a] as const });
    const POST = server({ get: (event, a) => new Promise((resolve) => resolve(a)) });
    fetchMock.mockImplementation((url, { body }) =>
      POST({
        url,
        request: { text: () => new Promise((resolve) => resolve(body)) },
      } as MyRequestEvent),
    );

    await expect(client.get(123)).resolves.toEqual(123);
    await expect(client.get(124)).resolves.toEqual(124);
  });

  it("should call the server and get an error back", async () => {
    const rpcBase = createRPCBase();
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");
    const { client, server } = factory({ get: (a: number) => [a] as const });
    const POST = server({
      get: (event, a) =>
        new Promise((resolve, reject) => {
          if (a === 123) {
            resolve(123);
          }

          reject(new Error("Something went terribly wrong"));
        }),
    });
    fetchMock.mockImplementation((url, { body }) =>
      POST({
        url,
        request: { text: () => new Promise((resolve) => resolve(body)) },
      } as MyRequestEvent),
    );

    await expect(client.get(123)).resolves.toEqual(123);
    await expect(client.get(1234)).rejects.toThrowError("Something went terribly wrong");
  });

  it("should call the server and get a custom error back", async () => {
    const rpcBase = createRPCBase({
      errorParser: {
        serialize(error) {
          if (error instanceof CustomError) {
            return {
              type: "CustomError",
              args: [`${error.message}: Extra info`],
            } as const;
          }

          return {
            type: "Error",
            args: [error.message],
          } as const;
        },
        deserialize(data) {
          if (data.type === "CustomError") {
            return new CustomError(...data.args);
          }

          return new Error(...data.args);
        },
      },
    });
    const factory = rpcBase<MyService, MyRequestEvent>("/foo/bar/baz");
    const { client, server } = factory({ get: (a: number) => [a] as const });
    const POST = server({
      get: (event, a) =>
        new Promise((resolve, reject) => {
          if (a === 123) {
            return resolve(123);
          }

          if (a === 1234) {
            return reject(new CustomError("Something went extra terribly wrong"));
          }

          return reject(new Error("Something went terribly wrong"));
        }),
    });
    fetchMock.mockImplementation((url, { body }) =>
      POST({
        url,
        request: { text: () => new Promise((resolve) => resolve(body)) },
      } as MyRequestEvent),
    );

    await expect(client.get(123)).resolves.toEqual(123);
    await expect(client.get(1234)).rejects.toThrowError(
      "Something went extra terribly wrong: Extra info",
    );
    await expect(client.get(12345)).rejects.toThrowError("Something went terribly wrong");
  });
});
