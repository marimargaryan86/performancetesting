export default abstract class JunctionPayService {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  protected makeRequest(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      queryParams?: Record<string, unknown>;
      headers?: Record<string, string>;
      data?: unknown;
      token?: string;
    } = {},
  ): Promise<Response> {
    const url = new URL(resource, this.baseUrl);

    if (options.queryParams) {
      Object.entries(options.queryParams).forEach(([key, val]) =>
        url.searchParams.set(key, `${val}`),
      );
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
