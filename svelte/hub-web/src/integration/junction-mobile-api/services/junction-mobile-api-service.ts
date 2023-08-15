import JunctionService from "integration/common/junction-service";

export default abstract class JunctionMobileApiService extends JunctionService {
  private readonly apiKey: string;

  constructor(baseUrl?: string, apiKey?: string) {
    super(baseUrl);

    this.apiKey = apiKey ?? "";
  }

  protected override makeRequest<TResp = unknown, TReq = unknown>(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      queryParams?: Record<string, unknown>;
      headers?: Record<string, string>;
      data?: TReq;
    } = {},
  ): Promise<Omit<Response, "json"> & { json: () => Promise<TResp> }> {
    return super.makeRequest(resource, { ...options, token: this.apiKey });
  }
}
