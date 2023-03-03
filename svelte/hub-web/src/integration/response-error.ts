import type { ResponseErrorSchema } from "./schemas/error";

export default class ResponseError extends Error {
  readonly response: ResponseErrorSchema;

  constructor(response: ResponseErrorSchema) {
    super("Response error");

    this.response = response;
  }
}
