import type { MaybePromise, RequestEvent } from "@sveltejs/kit";
import type { Callable, ClientCallable, ErrorData } from "../types";
import type { ClientMapping } from "../client";

export type ServerMapping<
  TRequestEvent extends RequestEvent,
  TServerMethods extends object,
  TClientMapping extends ClientMapping<TServerMethods>,
> = {
  [key in keyof (TServerMethods | TClientMapping)]: TServerMethods[key] extends Callable
    ? TClientMapping[key] extends ClientCallable
      ? (
          event: TRequestEvent,
          ...args: ReturnType<TClientMapping[key]>
        ) => MaybePromise<Awaited<ReturnType<TServerMethods[key]>>>
      : never
    : never;
};

export type ServerEndpoint<TRequestEvent extends RequestEvent> = (
  event: TRequestEvent,
) => MaybePromise<Response>;

export type ServerResponseData =
  | {
      success: true;
      data: unknown;
    }
  | {
      success: false;
      error?: ErrorData;
    };
