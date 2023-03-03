type ResourceURL = `/${string}`;

export default abstract class BaseService {
  private readonly baseUrl: string;
  private readonly headers = { "Content-Type": "application/vnd.api+json" };

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private getUrl(resource: string): URL {
    return new URL(resource, this.baseUrl);
  }

  protected get(resource: ResourceURL, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      method: "GET",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected post(resource: ResourceURL, data: unknown, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      body: JSON.stringify(data),
      method: "POST",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected patch(resource: ResourceURL, data: unknown, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      body: JSON.stringify(data),
      method: "PATCH",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected put(resource: ResourceURL, data: unknown, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      body: JSON.stringify(data),
      method: "PUT",
      headers: { ...this.headers, ...init?.headers },
    });
  }

  protected delete(resource: ResourceURL, init?: RequestInit): Promise<Response> {
    return fetch(this.getUrl(resource), {
      ...init,
      method: "DELETE",
      headers: { ...this.headers, ...init?.headers },
    });
  }
}
