import { env } from "$env/dynamic/public";

export class JunctionError extends Error {
  readonly json: unknown;
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
    response: { json: unknown; status: number; statusText: string },
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

    this.json = response.json;
    this.status = response.status;
  }
}

export async function createJunctionError(
  response: Response,
  options: ErrorOptions = {},
): Promise<JunctionError> {
  let json: unknown = undefined;

  try {
    json = await response.json();
  } catch {
    //
  }

  return new JunctionError(
    { json, status: response.status, statusText: response.statusText },
    options,
  );
}

export function ensureJunctionError(error: unknown): error is JunctionError {
  return error instanceof JunctionError;
}

export async function throwIfError(response: Response): Promise<void> {
  if (response.status >= 400) {
    const error = await createJunctionError(response);

    if (env.PUBLIC_DEV === "1") {
      // eslint-disable-next-line no-console
      console.debug(error);
    }

    throw error;
  }
}
