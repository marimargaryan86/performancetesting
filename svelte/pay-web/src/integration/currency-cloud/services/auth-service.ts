import type { AuthenticationSchema } from "../schemas/authentication";

export enum AuthServiceError {
  UNAUTHORIZED = 0,
}

export default class AuthService {
  private readonly apiBaseUrl: string;
  private readonly clientId: string;
  private readonly apiKey: string;
  private readonly ttlMs: number;
  private sessionToken = "";
  private sessionTokenExpiresAt = new Date(Date.now());
  private enabled = true;

  constructor(apiBaseUrl: string, clientId: string, apiKey: string, ttlMs = 1500000) {
    this.apiBaseUrl = apiBaseUrl;
    this.clientId = clientId;
    this.apiKey = apiKey;
    this.ttlMs = ttlMs;
  }

  async getSession(): Promise<string> {
    if (!this.enabled) {
      throw AuthServiceError.UNAUTHORIZED;
    }

    if (this.sessionToken && new Date(Date.now()) < this.sessionTokenExpiresAt) {
      return this.sessionToken;
    }

    this.sessionTokenExpiresAt = new Date(Date.now() + this.ttlMs);

    const resp = await fetch(new URL("/v2/authenticate/api", this.apiBaseUrl), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        login_id: this.clientId,
        api_key: this.apiKey,
      }),
    });

    switch (resp.status) {
      case 200:
        break;
      default:
        this.enabled = false;
        throw AuthServiceError.UNAUTHORIZED;
    }

    const data: AuthenticationSchema = await resp.json();

    this.sessionToken = data.auth_token;

    return this.sessionToken;
  }
}
