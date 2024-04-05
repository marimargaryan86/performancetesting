import type * as Generated from "./client/types/generated";

export type Operations<
  TSpecification extends Generated.Specification,
  TResource extends keyof TSpecification,
> = TSpecification[TResource];

export type Operation<
  TOperations extends Generated.Operations,
  TMethod extends keyof TOperations,
> = TOperations[TMethod] extends Generated.Operation ? TOperations[TMethod] : never;

export type Request<TOperation extends Generated.Operation> = Exclude<
  TOperation["request"],
  undefined
>;

type _RequestBody<
  TRequest extends Generated.Request,
  TContentType extends TBody["type"],
  TBody extends Generated.Body = Exclude<TRequest["body"], undefined>,
  TOut = Extract<TBody, { type: TContentType }>["data"],
> = unknown extends TOut ? never : TOut;

export type RequestBody<
  TRequest extends Generated.Request,
  TContentType extends Exclude<TRequest["body"], undefined>["type"],
> = _RequestBody<TRequest, TContentType>;

export type RequestParams<TRequest extends Generated.Request> = Omit<TRequest, "body">;

export type Response<TOperation extends Generated.Operation> = TOperation["response"];

export type _ResponseBody<
  TResponses extends Generated.Response,
  TStatus extends TResponses["status"],
  TContentType extends Exclude<TResponse["body"], undefined>["type"],
  TResponse extends Generated.Response = Extract<TResponses, { status: TStatus }>,
  TOut = Extract<Exclude<TResponse["body"], undefined>, { type: TContentType }>["data"],
> = TOut;

export type ResponseBody<
  TResponses extends Generated.Response,
  TStatus extends TResponses["status"],
  TContentType extends Exclude<Extract<TResponses, { status: TStatus }>["body"], undefined>["type"],
> = _ResponseBody<TResponses, TStatus, TContentType>;
