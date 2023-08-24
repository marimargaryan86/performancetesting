import { URLExtended } from "utils/url";

export default abstract class JunctionService {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? "";
  }

  protected static getCursor(data: {
    data: unknown[];
    links: { next: string };
  }): string | undefined {
    if (!data.data.length) {
      return undefined;
    }

    return new URL(data.links.next).searchParams.get("page[cursor]") ?? undefined;
  }

  protected makeRequest<TResp = unknown>(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      queryParams?: Record<string, string | number | undefined>;
      headers?: Record<string, string>;
      data?: unknown;
      token?: string;
    } = {},
  ): Promise<Omit<Response, "json"> & { json: () => Promise<TResp> }> {
    return fetch(
      new Request(new URLExtended(resource, { base: this.baseUrl, query: options.queryParams }), {
        headers: {
          "Content-Type": "application/vnd.api+json",
          ...(options.token ? { Authorization: `Bearer ${options.token}` } : undefined),
          ...options.headers,
        },
        method: options.method,
        body: options.data ? JSON.stringify(options.data) : undefined,
      }),
    );
  }
}
