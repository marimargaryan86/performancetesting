import type { ClientMapping, ClientMethods } from "./types";
import type { ErrorData, Callable, ClientCallable } from "../types";
import type { RPCBaseOptions } from "../rpc-base";
import type { ServerResponseData } from "../server";
export * from "./types";

export function getClient<
  TRouteId extends string,
  TServerMethods extends object,
  TClientMapping extends ClientMapping<TServerMethods>,
  TErrorData extends ErrorData,
>(
  route: TRouteId,
  mapping: TClientMapping,
  { requestParser, responseParser, errorParser }: RPCBaseOptions<TErrorData>,
): ClientMethods<TServerMethods, TClientMapping> {
  const methods: Record<string, Callable> = {};

  if (typeof window === "undefined") {
    return methods as ClientMethods<TServerMethods, TClientMapping>;
  }

  Object.entries(mapping).forEach(([method, func]) => {
    // Build URL
    const url = new URL(route, window.location.origin);
    url.searchParams.set("action", method);

    // Assign method
    methods[method] = async (...args): Promise<unknown> => {
      const resp = await fetch(url, {
        method: "POST",
        body: requestParser.stringify((func as ClientCallable)(...args)),
      });
      const data: ServerResponseData = responseParser.parse(await resp.text());

      if (data.success) {
        return data.data;
      }

      if (data.error) {
        throw errorParser.deserialize(data.error as TErrorData);
      }

      throw new Error("An unhandled error occurred");
    };
  });

  return methods as ClientMethods<TServerMethods, TClientMapping>;
}
