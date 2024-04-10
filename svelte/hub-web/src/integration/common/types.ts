import type { Specification, Operation } from "$lib/openapi/client/types/generated";
import type { HTTPMethod } from "$lib/openapi/resolvers/types";

export type GetResponse<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
  TMethod extends HTTPMethod,
  TStatus extends number,
> = TSpecification[TResource][TMethod] extends Operation
  ? Extract<TSpecification[TResource][TMethod]["response"], { status: TStatus }>
  : never;

export type GetOKResponse<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
> = NonNullable<GetResponse<TSpecification, TResource, "get", 200>["body"]>["data"];

export type GetCreatedResponse<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
> = NonNullable<GetResponse<TSpecification, TResource, "get", 201>["body"]>["data"];

export type PostOKResponse<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
> = NonNullable<GetResponse<TSpecification, TResource, "post", 200>["body"]>["data"];

export type PostCreatedResponse<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
> = NonNullable<GetResponse<TSpecification, TResource, "post", 201>["body"]>["data"];

export type GetIncluded<
  TResponse extends { included?: { type: string }[] },
  TType extends NonNullable<TResponse["included"]>[number]["type"],
> = Extract<NonNullable<TResponse["included"]>[number], { type: TType }>;

export type GetRequest<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
  TMethod extends HTTPMethod,
> = TSpecification[TResource][TMethod] extends Operation
  ? NonNullable<NonNullable<TSpecification[TResource][TMethod]["request"]>["body"]>["data"]
  : never;

export type PostRequest<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
> = GetRequest<TSpecification, TResource, "post">;

export type PatchRequest<
  TSpecification extends Specification,
  TResource extends keyof TSpecification,
> = GetRequest<TSpecification, TResource, "patch">;
