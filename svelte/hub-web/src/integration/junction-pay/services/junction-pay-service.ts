export default abstract class JunctionPayService {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    if (!baseUrl) {
      throw new Error("Base URL is not defined");
    }

    this.baseUrl = baseUrl;
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
      queryParams?: Record<string, unknown>;
      headers?: Record<string, string>;
      data?: unknown;
      token?: string;
    } = {},
  ): Promise<Omit<Response, "json"> & { json: () => Promise<TResp> }> {
    const url = new URL(resource, this.baseUrl);

    if (options.queryParams) {
      Object.entries(options.queryParams).forEach(([key, val]) => {
        if (val !== undefined) {
          url.searchParams.set(key, `${val}`);
        }
      });
    }

    return fetch(
      new Request(url, {
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
