import type { RequestEvent } from "@sveltejs/kit";
import type { ClientMapping } from "../client";
import type { ErrorData, Callable } from "../types";
import type { RPCBaseOptions } from "../rpc-base";
import type { ServerEndpoint, ServerMapping, ServerResponseData } from "./types";
export * from "./types";

export function getServer<
  TRequestEvent extends RequestEvent,
  TServerMethods extends object,
  TClientMapping extends ClientMapping<TServerMethods>,
  TErrorData extends ErrorData,
>({
  requestParser,
  responseParser,
  errorParser,
  onErrorResponse,
}: RPCBaseOptions<TErrorData>): (
  mapping: ServerMapping<TRequestEvent, TServerMethods, TClientMapping>,
) => ServerEndpoint<TRequestEvent> {
  return (mapping) => async (event) => {
    const action = event.url.searchParams.get("action") as keyof typeof mapping;
    const args = requestParser.parse(await event.request.text());

    try {
      return new Response(
        responseParser.stringify({
          success: true,
          data: await (mapping[action] as Callable)(event, ...args),
        } satisfies ServerResponseData),
      );
    } catch (err) {
      if (err instanceof Error) {
        onErrorResponse?.(event, err);

        return new Response(
          responseParser.stringify({
            success: false,
            error: errorParser.serialize(err as Error),
          } satisfies ServerResponseData),
        );
      }

      return new Response(
        responseParser.stringify({ success: false } satisfies ServerResponseData),
      );
    }
  };
}
