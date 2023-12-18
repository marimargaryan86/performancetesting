import * as devalue from "devalue";
import type { RequestEvent } from "../$types";
import { error } from "@sveltejs/kit";
import { ensureJunctionError } from "integration/common/junction-error";

/**
 * This function creates a client-side service for making API calls. You
 * provide it with a base URL, and it returns a service with methods
 * corresponding to different API actions. You can use these methods to make
 * API requests against the SvelteKit server.
 *
 * @template TService - The service interface representing the API methods.
 * @template TRoute - The base API route as a string.
 * @param {TRoute} route - The base URL for the API calls.
 * @returns A function that, when called with a mapping object, returns
 *          a service with methods for making SvelteKit API requests.
 */
export function clientServiceFactory<TService extends object, TRoute extends string>(
  route: TRoute,
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
): <TMapping extends Record<keyof TService, any[]>>(
  mapping: Record<keyof TService, true>,
) => {
  [key in keyof TService]: (
    ...params: TMapping[key]
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
  ) => TService[key] extends (...args: any[]) => infer TReturn ? TReturn : never;
} {
  return (mapping) => {
    const nextMapping = Object.fromEntries(
      Object.keys(mapping).map((method) => [
        method,
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        async (...args: any[]): Promise<any> => {
          const url = new URL(route, origin);
          url.searchParams.set("action", method);

          const resp = await fetch(url, { method: "POST", body: devalue.stringify(args) });

          if (resp.status !== 200) {
            throw new Error("An unexpected error occurred");
          }

          return devalue.parse(await resp.text());
        },
      ]),
    );

    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return nextMapping as any;
  };
}

/**
 * This function generates a SvelteKit server service that marshalls HTTP
 * request data and forwards the request to various integration instances. You
 * define functions for different API actions, and this factory creates a
 * handler that listens for these actions in incoming requests, executes the
 * corresponding function, and returns the response.
 *
 * @template TClient - A record type representing the client service interface.
 * @param {TClient} _ - The client interface (used for type inference).
 * @returns A function that takes server logic mappings and returns
 *          an async function to handle outgoing Junction API requests.
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export function serverServiceFactory<TClient extends Record<string, (...args: any[]) => any>>(
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  _: TClient,
): <
  TMapping extends {
    [key in keyof TClient]: (
      event: RequestEvent,
      ...args: Parameters<TClient[key]>
    ) => ReturnType<TClient[key]>;
  },
>(
  mapping: TMapping,
) => (event: RequestEvent) => Promise<Response> {
  return (mapping) => {
    return async (event) => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const args = devalue.parse(await event.request.text()) as any[];
      const action = event.url.searchParams.get("action")?.toString();

      if (!action || !(action in mapping)) {
        throw error(405);
      }

      const func = mapping[action];

      if (!func) {
        throw error(405);
      }

      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        return new Response(devalue.stringify(await func(event, ...(args as any))));
      } catch (err) {
        if (ensureJunctionError(err)) {
          throw error(err.status, { message: err.message });
        }

        throw error(500);
      }
    };
  };
}
