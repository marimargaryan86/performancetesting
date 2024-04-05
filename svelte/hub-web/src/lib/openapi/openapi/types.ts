export interface SpecificationExtension {
  [key: `x-${string}`]: unknown;
}

export interface OpenAPIObject extends SpecificationExtension {
  openapi: string;
  info: InfoObject;
  servers?: ServerObject[];
  paths: PathsObject;
  components?: ComponentsObject;
  security?: SecurityRequirementObject[];
  tags?: TagObject[];
  externalDocs?: ExternalDocumentationObject;
}

export interface InfoObject extends SpecificationExtension {
  title: string;
  description?: string;
  termsOfService?: string;
  contact?: ContactObject;
  license?: LicenseObject;
  version: string;
}

export interface ContactObject extends SpecificationExtension {
  name?: string;
  url?: string;
  email?: string;
}

export interface LicenseObject extends SpecificationExtension {
  name: string;
  url?: string;
}

export interface ServerObject extends SpecificationExtension {
  url: string;
  description?: string;
  variable?: Record<string, ServerVariableObject>;
}

export interface ServerVariableObject extends SpecificationExtension {
  enum?: string[];
  default: string;
  description?: string;
}

export interface ComponentsObject extends SpecificationExtension {
  schemas?: Record<string, SchemaObject | ReferenceObject>;
  responses?: Record<string, ResponseObject | ReferenceObject>;
  parameters?: Record<string, ParameterObject | ReferenceObject>;
  examples?: Record<string, ExampleObject | ReferenceObject>;
  requestBodies?: Record<string, RequestBodyObject | ReferenceObject>;
  headers?: Record<string, HeaderObject | ReferenceObject>;
  securitySchemes?: Record<string, SecuritySchemeObject | ReferenceObject>;
  links?: Record<string, LinkObject | ReferenceObject>;
  callbacks?: Record<string, CallbackObject | ReferenceObject>;
}

export interface PathsObject extends SpecificationExtension {
  [path: `/${string}`]: PathItemObject;
}

export const methods = [
  "get",
  "put",
  "post",
  "delete",
  "options",
  "head",
  "patch",
  "trace",
] as const;
export type Method = (typeof methods)[number];

export interface PathItemObject extends Partial<ReferenceObject> {
  summary?: string;
  description?: string;
  get?: OperationObject;
  put?: OperationObject;
  post?: OperationObject;
  delete?: OperationObject;
  options?: OperationObject;
  head?: OperationObject;
  patch?: OperationObject;
  trace?: OperationObject;
  servers?: ServerObject[];
  parameters?: (ParameterObject | ReferenceObject)[];
}

export interface OperationObject {
  tags?: string[];
  summary?: string;
  description?: string;
  externalDocs?: ExternalDocumentationObject;
  operationId?: string;
  parameters?: (ParameterObject | ReferenceObject)[];
  requestBody?: RequestBodyObject | ReferenceObject;
  responses: ResponsesObject;
  callbacks?: Record<string, CallbackObject | ReferenceObject>;
  deprecated?: boolean;
  security?: SecurityRequirementObject[];
  servers?: ServerObject[];
}

export interface ExternalDocumentationObject {
  description?: string;
  url: string;
}

type Style =
  | "matrix"
  | "label"
  | "form"
  | "simple"
  | "spaceDelimited"
  | "pipeDelimited"
  | "deepObject";

export interface ParameterObject extends SpecificationExtension {
  name: string;
  in: "query" | "header" | "path" | "cookie";
  description?: string;
  required?: boolean;
  deprecated?: boolean;
  allowReserved?: boolean;
  allowEmptyValue?: boolean;
  style?: Style;
  explode?: boolean;
  example?: unknown;
  examples?: Record<string, ExampleObject | ReferenceObject>;
  schema?: SchemaObject | ReferenceObject;
  content?: Record<string, MediaTypeObject>;
}

export interface RequestBodyObject extends SpecificationExtension {
  description?: string;
  content: Record<string, MediaTypeObject>;
  required?: boolean;
}

export interface MediaTypeObject extends SpecificationExtension {
  schema?: SchemaObject | ReferenceObject;
  example?: unknown;
  examples?: Record<string, ExampleObject | ReferenceObject>;
  encoding?: Record<string, EncodingObject>;
}

export interface EncodingObject extends SpecificationExtension {
  contentType?: string;
  headers?: Record<string, HeaderObject | ReferenceObject>;
  style?: Style;
  explode?: boolean;
  allowReserved?: boolean;
}

export interface ResponsesObject extends SpecificationExtension {
  default?: ResponseObject | ReferenceObject;
  [httpStatus: `${number}`]: ResponseObject | ReferenceObject;
}

export interface ResponseObject extends SpecificationExtension {
  description: string;
  headers?: Record<string, HeaderObject | ReferenceObject>;
  content?: Record<string, MediaTypeObject>;
  links?: Record<string, LinkObject | ReferenceObject>;
}

export interface CallbackObject extends SpecificationExtension {
  [expression: `{${string}}`]: PathItemObject;
}

export interface ExampleObject extends SpecificationExtension {
  summary?: string;
  description?: string;
  value?: unknown;
  externalValue?: string;
}

export interface LinkObject extends SpecificationExtension {
  operationRef?: string;
  operationId?: string;
  parameters?: Record<string, unknown>;
  requestBody?: unknown;
  description?: string;
  server?: ServerObject;
}

export interface HeaderObject extends Omit<ParameterObject, "in" | "name"> {}

export interface TagObject extends SpecificationExtension {
  name: string;
  description?: string;
  externalDocs?: ExternalDocumentationObject;
}

export interface ReferenceObject {
  $ref: string;
}

export interface SchemaObject extends SpecificationExtension {
  type?: "string" | "object" | "number" | "integer" | "array" | "boolean" | "null";
  title?: string;
  allOf?: (SchemaObject | ReferenceObject)[];
  oneOf?: (SchemaObject | ReferenceObject)[];
  anyOf?: (SchemaObject | ReferenceObject)[];
  not?: SchemaObject | ReferenceObject;
  description?: string;
  default?: unknown;
  nullable?: boolean;
  discriminator?: DiscriminatorObject;
  readOnly?: boolean;
  writeOnly?: boolean;
  xml?: XMLObject;
  externalDocs?: ExternalDocumentationObject;
  example?: unknown;
  deprecated?: boolean;
  enum?: unknown[];
  required?: string[];
  maxLength?: number;
  minLength?: number;
  pattern?: string;
  format?: string;
  properties?: Record<string, SchemaObject | ReferenceObject>;
  additionalProperties?: boolean | SchemaObject | ReferenceObject;
  maxProperties?: number;
  minProperties?: number;
  multipleOf?: number;
  maximum?: number;
  exclusiveMaximum?: number;
  minimum?: number;
  exclusiveMinimum?: number;
  items?: SchemaObject | ReferenceObject;
  maxItems?: number;
  minItems?: number;
  uniqueItems?: boolean;
}

export interface DiscriminatorObject extends SpecificationExtension {
  propertyName: string;
  mapping?: Record<string, string>;
}

export interface XMLObject extends SpecificationExtension {
  name?: string;
  namespace?: string;
  prefix?: string;
  attribute?: boolean;
  wrapped?: boolean;
}

export interface SecuritySchemeObject extends SpecificationExtension {
  type: "http" | "apiKey" | "oauth2" | "openIdConnect";
  description?: string;
}

export interface SecuritySchemeHttpObject extends SecuritySchemeObject {
  type: "http";
  scheme: string;
  bearerFormat?: string;
}

export interface SecuritySchemeApiKeyObject extends SecuritySchemeObject {
  type: "apiKey";
  name: string;
  in: "query" | "header" | "cookie";
}

export interface SecuritySchemeOAuth2Object extends SecuritySchemeObject {
  type: "oauth2";
  flows: OAuthFlowsObject;
}

export interface SecuritySchemeOpenIdConnectObject extends SecuritySchemeObject {
  type: "openIdConnect";
  openIdConnectUrl: string;
}

export interface OAuthFlowsObject extends SpecificationExtension {
  implicit?: {
    authorizationUrl: string;
    tokenUrl: string;
    refreshUrl?: string;
    scopes?: Record<string, string>;
  };
  password?: {
    tokenUrl: string;
  };
  clientCredentials?: {
    tokenUrl: string;
  };
  authorizationCode?: {
    authorizationUrl: string;
    tokenUrl: string;
  };
}

export interface SecurityRequirementObject {
  [name: string]: string[];
}
