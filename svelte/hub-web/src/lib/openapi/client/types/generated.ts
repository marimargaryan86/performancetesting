import type { HTTPMethod } from "../../resolvers/types";

export type Body = {
  type: string;
  data: unknown;
};

export type Request = {
  cookie?: Record<string, unknown>;
  headers?: Record<string, unknown>;
  path?: Record<string, unknown>;
  query?: Record<string, unknown>;
  body?: Body;
};

export type Response = {
  status: "default" | number;
  body?: Body;
  headers?: Record<string, unknown>;
};

export type Operation = {
  request?: Request;
  response: Response;
};

export type Operations = Partial<Record<HTTPMethod, Operation>>;

export type Specification = Record<string, Operations>;
