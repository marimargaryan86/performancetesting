import { URLExtended } from "$lib/utils/url";

export default abstract class OryService {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? "";
  }

  protected async makeRequest<TResp = unknown>(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      queryParams?: Record<string, string | number | undefined>;
      headers?: Record<string, string>;
      cookies?: Record<string, string>;
      data?: unknown;
    } = {},
  ): Promise<Omit<Response, "json"> & { json: TResp }> {
    const resp = await fetch(
      new Request(new URLExtended(resource, { base: this.baseUrl, query: options.queryParams }), {
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json",
          ...options.headers,
          ...(options.cookies
            ? {
                cookie: Object.entries(options.cookies)
                  .map(([key, val]) => `${key}=${val}`)
                  .join("; "),
              }
            : {}),
        },
        method: options.method ?? "GET",
        body: options.data ? JSON.stringify(options.data) : undefined,
      }),
    );

    let json: TResp | undefined = undefined;

    try {
      json = await resp.json();
    } catch {
      //
    }

    return Object.assign(resp, { json });
  }
}
