export type MaybePromise<T> = T | Promise<T>;

export const httpMethods = [
  "get",
  "put",
  "post",
  "delete",
  "options",
  "head",
  "patch",
  "trace",
] as const;

export type HTTPMethod = (typeof httpMethods)[number];

export interface DiscriminatorObject {
  propertyName: string;
  mapping?: Record<string, string>;
}

export interface SchemaObject {
  read?: string;
  write?: string;
}

export interface EncodingObject {
  contentType?: string;
  headers?: Record<string, ParameterObject>;
}

export interface MediaTypeObject {
  schema?: SchemaObject;
  encoding?: Record<string, EncodingObject>;
}

export interface ParameterObject {
  in: "query" | "header" | "path" | "cookie";
  name: string;
  required: boolean;
  schema?: SchemaObject;
  content?: Record<string, MediaTypeObject>;
}

export interface RequestBodyObject {
  content: Record<string, MediaTypeObject>;
  required: boolean;
}

export interface ResponseObject {
  headers?: Record<string, ParameterObject>;
  content?: Record<string, MediaTypeObject>;
}

export interface ResponsesObject {
  default?: ResponseObject;
  [httpStatus: `${number}`]: ResponseObject;
}

export interface OperationObject {
  parameters: {
    cookie?: Record<string, ParameterObject>;
    query?: Record<string, ParameterObject>;
    header?: Record<string, ParameterObject>;
    path?: Record<string, ParameterObject>;
  };
  requestBody?: RequestBodyObject;
  responses: ResponsesObject;
}

export interface PathItemObject extends Partial<Record<HTTPMethod, OperationObject>> {}

export interface PathsObject {
  [path: `/${string}`]: PathItemObject;
}

export interface ComponentsObject {
  headers: Record<string, ParameterObject>;
  parameters: Record<string, ParameterObject>;
  requestBodies: Record<string, RequestBodyObject>;
  responses: Record<string, ResponseObject>;
  schemas: Record<string, SchemaObject>;
}

export interface OpenAPIObject {
  paths: PathsObject;
  components?: ComponentsObject;
}
