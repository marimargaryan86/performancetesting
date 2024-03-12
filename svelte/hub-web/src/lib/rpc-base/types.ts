import type { RequestEvent } from "@sveltejs/kit";

/** Get the SvelteKit route ID of a RequestEvent */
export type ExtractRouteId<TRequestEvent extends RequestEvent> =
  TRequestEvent extends RequestEvent<infer _, infer RouteId>
    ? RouteId extends string
      ? RouteId
      : never
    : never;

/* eslint-disable @typescript-eslint/no-explicit-any */
export type Callable = (...args: any[]) => any;

export type ClientCallable = (...args: any[]) => any[];

export type ErrorData = { type: string; args: any[] };
/* eslint-enable @typescript-eslint/no-explicit-any */

export type PayloadParser = {
  /* eslint-disable @typescript-eslint/no-explicit-any */
  stringify: (data: any) => string;
  parse: (data: string) => any;
  /* eslint-enable @typescript-eslint/no-explicit-any */
};

export type ErrorParser<TErrorData extends ErrorData> = {
  serialize: (error: Error) => TErrorData;
  deserialize: (data: TErrorData) => Error;
};

export type DefaultErrorData = { type: "Error"; args: [string] };
