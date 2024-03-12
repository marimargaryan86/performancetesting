import type { RequestEvent } from "@sveltejs/kit";
import type { ClientMapping, ClientMethods } from "../client/types";
import type { ErrorData, ErrorParser, PayloadParser, ExtractRouteId } from "../types";
import type { ServerEndpoint, ServerMapping } from "../server";

export type RPCBaseFactory<TServerMethods extends object, TRequestEvent extends RequestEvent> = <
  TClientMapping extends ClientMapping<TServerMethods>,
>(
  /**
   * Definition of the client methods, the returned arrays will be passed as arguments to the server
   * @example
   * ```ts
   * {
   *   get: (a: number, b: string) => [a, b] as const,
   * }
   * ```
   */
  mapping: TClientMapping,
) => {
  /**
   * Collection of the client side methods
   * @example
   * ```ts
   * // my-service.ts
   * export { server };
   * export default client;
   * ```
   */
  client: ClientMethods<TServerMethods, TClientMapping>;
  /**
   * Function to create the corresponding server side integration
   * @example
   * ```ts
   * // +server.ts
   * import { server } from "./my-service.ts";
   *
   * export const POST = server({
   *   get: (event, ...args) => "Foo",
   * });
   * ```
   * */
  server: (
    mapping: ServerMapping<TRequestEvent, TServerMethods, TClientMapping>,
  ) => ServerEndpoint<TRequestEvent>;
};

export type RPCBase = <TServerMethods extends object, TRequestEvent extends RequestEvent>(
  /** The SvelteKit server route */
  route: ExtractRouteId<TRequestEvent>,
) => RPCBaseFactory<TServerMethods, TRequestEvent>;

export type RPCBaseOptions<TErrorData extends ErrorData> = {
  requestParser: PayloadParser;
  responseParser: PayloadParser;
  errorParser: ErrorParser<TErrorData>;
  onErrorResponse?: (event: RequestEvent, error: Error) => void;
};
