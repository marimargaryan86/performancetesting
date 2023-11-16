import { getCookiesFromHeaders, type Cookie } from "utils/cookies";
import { URLExtended } from "utils/url";
import {
  loginFormParser,
  type LoginForm,
  type LoginFormSchema,
  type UserSchema,
  userParser,
  type SessionExtended,
} from "../schemas";

export default class OryService {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? "";
  }

  private makeRequest<TResponse = unknown>(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      cookies?: { name: string; value: string }[];
      queryParams?: Record<string, string | number | undefined>;
      data?: unknown;
    } = {},
  ): Promise<Omit<Response, "json"> & { json(): Promise<TResponse> }> {
    const url = new URLExtended(resource, { base: this.baseUrl, query: options.queryParams });

    return fetch(url, {
      body: options.data ? JSON.stringify(options.data) : undefined,
      method: options.method,
      credentials: "include",
      headers: {
        accept: "application/json",
        "content-type": "application/json",
        ...(options.cookies?.length
          ? {
              cookie: options.cookies.map(({ name, value }) => `${name}=${value}`).join("; "),
            }
          : {}),
      },
    });
  }

  async authenticate({
    cookies,
    flowId,
    data,
  }: {
    cookies: { name: string; value: string }[];
    flowId: string;
    data: Record<string, string>;
  }): Promise<SessionExtended> {
    const resp = await this.makeRequest<UserSchema>("/self-service/login", {
      queryParams: { flow: flowId },
      method: "POST",
      cookies,
      data,
    });

    if (resp.status !== 200) {
      throw new Error("Unauthorized");
    }

    const respCookies = getCookiesFromHeaders(resp.headers);
    const sessionCookie = respCookies.find((cookie) => cookie.name.startsWith("ory_session_"));

    if (!sessionCookie) {
      throw new Error("Unauthorized");
    }

    const respData = await resp.json();

    return {
      id: sessionCookie.name,
      token: sessionCookie.value,
      expiresAt: new Date(respData.session.expires_at),
      user: userParser.toModel(respData),
    };
  }

  async getLoginForm(): Promise<{
    cookies: Cookie[];
    form: LoginForm;
  }> {
    const resp = await this.makeRequest<LoginFormSchema>("/self-service/login/browser");

    return {
      cookies: getCookiesFromHeaders(resp.headers),
      form: loginFormParser.toModel(await resp.json()),
    };
  }
}
