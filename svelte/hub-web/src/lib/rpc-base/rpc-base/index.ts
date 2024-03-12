import type { RequestEvent } from "@sveltejs/kit";
import type { DefaultErrorData, ErrorData, ErrorParser, ExtractRouteId } from "../types";
import type { RPCBase, RPCBaseFactory, RPCBaseOptions } from "./types";
import { getClient } from "../client";
import { getServer } from "../server";
export * from "./types";

function getRPCBaseFactory<
  TServerMethods extends object,
  TRequestEvent extends RequestEvent,
  TErrorData extends ErrorData,
>(
  route: ExtractRouteId<TRequestEvent>,
  options: RPCBaseOptions<TErrorData>,
): RPCBaseFactory<TServerMethods, TRequestEvent> {
  return (mapping) => ({
    client: getClient(route, mapping, options),
    server: getServer(options),
  });
}

const DEFAULT_ERROR_PARSER: ErrorParser<DefaultErrorData> = {
  serialize(error) {
    return {
      type: "Error",
      args: [error.message],
    } as const;
  },
  deserialize(data) {
    return new Error(data.args.toString());
  },
};

/**
 * Create a RPC base
 * @param param0 RPC base options. `requestParser`: the method or serializing/deserializing
 * method parameters when sending from the client and receiving on the server. `responseParser`:
 * the method of serializing/deserializing method responses when sending from the server and
 * receiving on the client. `errorParser`: the method of serializing/deserialzigin error thrown
 * by the server method.
 * @returns A RPC base.
 */
export function createRPCBase<TErrorData extends ErrorData = DefaultErrorData>({
  requestParser = JSON,
  responseParser = JSON,
  errorParser = DEFAULT_ERROR_PARSER as unknown as ErrorParser<TErrorData>,
  onErrorResponse,
}: Partial<RPCBaseOptions<TErrorData>> = {}): RPCBase {
  return (route) =>
    getRPCBaseFactory(route, {
      requestParser,
      responseParser,
      errorParser,
      onErrorResponse,
    });
}
