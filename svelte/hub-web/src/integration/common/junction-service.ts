import { URLExtended } from "utils/url";
import { throwIfError } from "./junction-error";
import type { Session } from "integration/ory/schemas/authentication";

/**
 * This abstract base class is a foundational service layer for making RESTful
 * HTTP requests to Junction APIs; a specific API service `extends` from this.
 * Included are handlers for requests, errors, and authentication.
 */
export default abstract class JunctionService {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? "";
  }

  /**
   * Gets pagination cursors from API response data.
   *
   * @static
   * @param {{ data: unknown[]; links: { next: string } }} data - The API response data.
   * @returns {string | undefined} The cursor value or undefined if not found.
   */
  protected static getCursor(data: {
    data: unknown[];
    links: { next: string };
  }): string | undefined {
    if (!data.data.length) {
      return undefined;
    }

    return new URL(data.links.next).searchParams.get("page[cursor]") ?? undefined;
  }

  /**
   * Makes an HTTP request to the API.
   *
   * @protected
   * @async
   * @template TResp - The expected response data type.
   * @param {string} resource - The API resource or endpoint.
   * @param {RequestOptions} [options={}] - Request options, including method, query parameters, headers, data, session, and token.
   * @returns {Promise<Omit<Response, "json"> & { json: TResp }>} A promise with the response and parsed JSON data.
   */
  protected async makeRequest<TResp = unknown>(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      queryParams?: Record<string, string | number | undefined>;
      headers?: Record<string, string>;
      data?: unknown;
      session: Session;
    },
  ): Promise<Omit<Response, "json"> & { json: TResp }> {
    const resp = await fetch(
      new Request(new URLExtended(resource, { base: this.baseUrl, query: options.queryParams }), {
        headers: {
          "Content-Type": "application/vnd.api+json",
          ...options.headers,
          cookie: `ory_kratos_session=${options.session.token}`,
        },
        method: options.method,
        body: options.data ? JSON.stringify(options.data) : undefined,
      }),
    );

    await throwIfError(resp);

    let json: TResp | undefined = undefined;

    try {
      json = await resp.json();
    } catch {
      //
    }

    return { ...resp, json: json as TResp };
  }
}
