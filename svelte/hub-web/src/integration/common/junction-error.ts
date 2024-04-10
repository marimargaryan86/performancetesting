import { dev } from "$app/environment";

type Pointer<
  TSchema,
  TRecord = TSchema extends Record<string, unknown>
    ? { [key in keyof TSchema as string extends key ? never : key]: key }
    : never,
  TKeys extends keyof TRecord = keyof TRecord,
> = {
  [key in TKeys]: key extends string
    ? key extends keyof TSchema
      ? `/${key}${Pointer<TSchema[key]>}`
      : ""
    : never;
}[TKeys];

export type ApiError<TSchema> = {
  errors: {
    status: string;
    title?: string;
    detail: string;
    code?: string;
    source?: {
      pointer?: Pointer<TSchema>;
      parameter?: string;
      header?: string;
    };
  }[];
};

export class JunctionError<TSchema> extends Error {
  readonly traceId?: string;
  readonly requestId?: string;
  readonly json?: ApiError<TSchema>;
  readonly status: number;

  get badRequest(): boolean {
    return this.status === 400;
  }

  get unauthorized(): boolean {
    return this.status === 401;
  }

  get forbidden(): boolean {
    return this.status === 403;
  }

  get notFound(): boolean {
    return this.status === 404;
  }

  get unprocessableContent(): boolean {
    return this.status === 422;
  }

  get internalServerError(): boolean {
    return this.status === 500;
  }

  get badGateway(): boolean {
    return this.status === 502;
  }

  get serviceUnavailable(): boolean {
    return this.status === 503;
  }

  constructor(
    response: {
      traceId?: string;
      requestId?: string;
      json?: ApiError<TSchema>;
      status: number;
      statusText: string;
    },
    options: ErrorOptions = {},
  ) {
    super(
      JSON.stringify({
        status: response.status,
        message: response.statusText,
        body: response.json,
      }),
      options,
    );

    this.traceId = response.traceId;
    this.requestId = response.requestId;
    this.json = response.json;
    this.status = response.status;
  }
}

export async function createJunctionError<TSchema>(
  response: Response,
  options: ErrorOptions = {},
): Promise<JunctionError<TSchema>> {
  let json: ApiError<TSchema> | undefined = undefined;

  try {
    json = await response.json();
  } catch {
    //
  }

  return new JunctionError(
    {
      traceId: response.headers.get("x-trace-id") ?? undefined,
      requestId: response.headers.get("x-request-id") ?? undefined,
      json,
      status: response.status,
      statusText: response.statusText,
    },
    options,
  );
}

export function ensureJunctionError<TSchema>(error: unknown): error is JunctionError<TSchema> {
  return error instanceof JunctionError;
}

export async function throwIfError(response: Response): Promise<void> {
  if (response.status >= 400) {
    const error = await createJunctionError(response);

    if (dev) {
      // eslint-disable-next-line no-console
      console.debug(error);
    }

    throw error;
  }
}
