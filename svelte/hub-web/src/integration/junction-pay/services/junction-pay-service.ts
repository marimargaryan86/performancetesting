export default abstract class JunctionPayService {
  private readonly baseUrl: string;
  protected readonly headers = {
    "Content-Type": "application/vnd.api+json",
  };

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  protected getHeadersWithAuth(token: string): Record<string, string> {
    return {
      ...this.headers,
      Authorization: `Bearer ${token}`,
    };
  }

  protected getResourceUrl(resource: string, queryParams?: Record<string, unknown>): URL {
    const url = new URL(resource, this.baseUrl);

    if (queryParams) {
      Object.entries(queryParams).forEach(([key, val]) => url.searchParams.set(key, `${val}`));
    }

    return url;
  }
}
