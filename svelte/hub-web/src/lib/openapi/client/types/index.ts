import type * as Generated from "./generated";

export type FetchParams = {
  path?: Record<string, unknown>;
  query?: Record<string, unknown>;
};

export type FetchHeadersInit = {
  accept?: string;
  "content-type"?: string;
  cookie?: Record<string, unknown>;
  [key: string]: unknown;
};

export type FetchRequestInit = {
  headers?: FetchHeadersInit;
  body?: unknown;
} & Omit<RequestInit, "headers" | "body">;

type ExtractBody<T> = T extends { body?: Generated.Body } ? Exclude<T["body"], undefined> : never;

type RequestPick<
  T extends Generated.Request | undefined,
  TKeys extends keyof Generated.Request,
  TRequest extends Generated.Request = Exclude<T, undefined>,
> = Omit<TRequest, Exclude<keyof TRequest, TKeys>>;

type RequestHeaders<
  T extends Generated.Request | undefined,
  THeaders extends Record<string, unknown> = RequestPick<T, "headers">,
> =
  | { [key in keyof THeaders]: THeaders[key] }[keyof THeaders]
  | (keyof THeaders extends never ? NonNullable<unknown> : never);

export type Fetch<TSpecification extends Generated.Specification> = <
  TResource extends keyof TSpecification,
  TMethod extends keyof TSpecification[TResource],
  TAccept extends ExtractBody<TOperation["response"]>["type"],
  TContentType extends TOperation["request"] extends Generated.Request
    ? ExtractBody<TOperation["request"]>["type"]
    : never,
  TOperation extends
    Generated.Operation = TSpecification[TResource][TMethod] extends Generated.Operation
    ? TSpecification[TResource][TMethod]
    : never,
>(
  {
    resource,
    ...params
  }: {
    resource: TResource;
  } & RequestPick<TOperation["request"], "path" | "query">,
  init?: {
    method?: TMethod;
    headers?: {
      accept?: TAccept;
      "content-type"?: TContentType;
    } & RequestPick<TOperation["request"], "cookie"> &
      RequestHeaders<TOperation["request"]>;
    body?: TOperation["request"] extends Generated.Request
      ? Extract<ExtractBody<TOperation["request"]>, { type: TContentType }>["data"]
      : never;
  } & Omit<RequestInit, "method" | "body" | "headers">,
) => Promise<
  {
    [response in TOperation["response"] as response["status"]]: {
      status: response["status"];
      json(): Promise<Extract<response["body"], { type: TAccept }>["data"]>;
    };
  }[TOperation["response"]["status"]] &
    Omit<Response, "status" | "json">
>;
