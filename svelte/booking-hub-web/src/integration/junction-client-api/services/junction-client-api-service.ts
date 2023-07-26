export default abstract class JunctionClientApiService {
  private readonly baseUrl: string;
  private readonly apiKey: string;

  constructor(baseUrl: string, apiKey: string) {
    this.baseUrl = baseUrl;
    this.apiKey = apiKey;
  }

  protected makeRequest(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      queryParams?: Record<string, unknown>;
      headers?: Record<string, string>;
      data?: unknown;
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
          Authorization: `Bearer ${this.apiKey}`,
          ...options.headers,
        },
        method: options.method,
        body: options.data ? JSON.stringify(options.data) : undefined,
      }),
    );
  }
}
