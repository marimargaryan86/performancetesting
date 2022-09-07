import type AuthService from "./auth-service";

export default abstract class BaseService {
  private readonly apiBaseUrl: string;
  private readonly authService: AuthService;

  constructor(apiBaseUrl: string, authService: AuthService) {
    this.apiBaseUrl = apiBaseUrl;
    this.authService = authService;
  }

  protected async fetch(
    url: URL | string,
    init?: RequestInit,
    params?: Record<string, unknown>,
  ): Promise<Response> {
    const init_ = {
      ...init,
      headers: { ...init?.headers, "X-Auth-Token": await this.authService.getSession() },
    };

    const url_ = new URL(url, this.apiBaseUrl);

    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined) {
          url_.searchParams.set(key, (value as { toString: () => string }).toString());
        }
      });
    }

    return fetch(url_, init_);
  }
}
