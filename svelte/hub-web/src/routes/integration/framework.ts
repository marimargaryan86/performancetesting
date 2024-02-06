import * as devalue from "devalue";
import { error, type MaybePromise, type RequestEvent } from "@sveltejs/kit";
import { ensureJunctionError } from "~/integration/common/junction-error";
import { browser } from "$app/environment";
import { z } from "zod";

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyFunc = (...args: any[]) => any;

type ClientMethod<TMethod, TServiceMethod> = TMethod extends AnyFunc
  ? TServiceMethod extends AnyFunc
    ? (...args: Parameters<TMethod>) => Promise<Awaited<ReturnType<TServiceMethod>>>
    : never
  : never;

type ClientServiceFactory<TService extends object> = <
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  TMapping extends { [key in keyof TService]?: (...args: any[]) => any[] },
>(
  mapping: TMapping,
) => {
  [key in keyof Pick<
    TService,
    keyof TMapping extends keyof TService ? keyof TMapping : never
  >]: ClientMethod<TMapping[key], TService[key]>;
};

type ServerServiceFactory<TClient extends Record<string, AnyFunc>> = (mapping: {
  [key in keyof TClient]: (
    event: RequestEvent,
    ...args: Parameters<TClient[key]>
  ) => MaybePromise<Awaited<ReturnType<TClient[key]>>>;
}) => (event: RequestEvent) => Promise<Response>;

/**
 * Get a fetch function for the client service
 *
 * @param route Route of the server client
 * @param action Uniquely identifying action name
 * @param func Function to determine the fetch payload, must return an array of its own arguments
 * @returns A client service fetch function
 */
function getFetchFunc(route: string, action: string, func: AnyFunc): AnyFunc {
  if (!browser) {
    return () => {
      throw new Error("Cannot be called on the server");
    };
  }

  const url = new URL(route, origin);
  url.searchParams.set("action", action);

  return async (...args) => {
    const resp = await fetch(url, {
      method: "POST",
      body: devalue.stringify(func(...args)),
    });

    if (resp.status === 200) {
      return devalue.parse(await resp.text());
    }

    if (resp.status === 400) {
      throw new z.ZodError(await devalue.parse(await resp.text()));
    }

    throw new Error(`Service error (${resp.statusText}): ${await resp.text()}`);
  };
}

/**
 * This function creates a client-side service for making API calls. You
 * provide it with a base URL, and it returns a service with methods
 * corresponding to different API actions. You can use these methods to make
 * API requests against the SvelteKit server.
 *
 * @template TService - The service interface representing the API methods.
 * @template TRoute - The base API route as a string.
 * @param {TRoute} route - The URL for the API calls.
 * @returns A function that, when called with a mapping object, returns
 *          a service with methods for making SvelteKit API requests.
 */
export function clientServiceFactory<TService extends object, TRoute extends string>(
  route: TRoute,
): ClientServiceFactory<TService> {
  return ((mapping) =>
    Object.fromEntries(
      Object.entries(mapping).map(([method, func]) => [
        method,
        getFetchFunc(route, method, func as AnyFunc),
      ]),
    )) as ClientServiceFactory<TService>;
}

/**
 * This function generates a SvelteKit server service that marshalls HTTP
 * request data and forwards the request to various integration instances. You
 * define functions for different API actions, and this factory creates a
 * handler that listens for these actions in incoming requests, executes the
 * corresponding function, and returns the response.
 *
 * @template TClient - A record type representing the client service interface.
 * @param {TClient} clientService - The client interface (used for type inference).
 * @returns A function that takes server logic mappings and returns
 *          an async function to handle outgoing Junction API requests.
 */
export function serverServiceFactory<TClient extends Record<string, AnyFunc>>(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  clientService: TClient,
): ServerServiceFactory<TClient> {
  return ((mapping) => async (event) => {
    const action = event.url.searchParams.get("action")?.toString();
    const method = mapping[action ?? ""];

    if (!method) {
      throw error(405);
    }

    try {
      const result = await method(event, ...devalue.parse(await event.request.text()));

      return new Response(devalue.stringify(result));
    } catch (err) {
      if (ensureJunctionError(err)) {
        event.setHeaders({
          "x-request-id": err.requestId ?? "unknown",
          "x-trace-id": err.traceId ?? "unknown",
        });
        throw error(err.status, { message: err.message });
      }

      if (err instanceof z.ZodError) {
        return new Response(devalue.stringify(err.issues), { status: 400 });
      }

      if (err instanceof Error) {
        throw error(500, { message: err.message });
      }

      throw error(500, { message: "An unexpected error occured" });
    }
  }) as ServerServiceFactory<TClient>;
}
