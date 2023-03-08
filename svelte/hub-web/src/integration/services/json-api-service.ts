export default abstract class JsonApiService {
  private readonly baseUrl: string;
  private readonly headers = { "Content-Type": "application/vnd.api+json" };

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getUrl(resource: string): URL {
    return new URL(resource, this.baseUrl);
  }

  protected get(resource: string, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      method: "GET",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected post(resource: string, data: unknown, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      body: JSON.stringify(data),
      method: "POST",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected patch(resource: string, data: unknown, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      body: JSON.stringify(data),
      method: "PATCH",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected put(resource: string, data: unknown, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      body: JSON.stringify(data),
      method: "PUT",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected delete(resource: string, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      method: "DELETE",
      headers: { ...this.headers, ...init?.headers },
    });
  }
}
