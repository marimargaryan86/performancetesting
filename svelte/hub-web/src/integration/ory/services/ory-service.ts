import { getCookiesFromHeaders, type Cookie } from "utils/cookies";
import { URLExtended } from "utils/url";
import type { SessionModel } from "models/user";
import {
  loginFormParser,
  type LoginForm,
  type LoginFormSchema,
  orySessionParser,
  type OrySessionSchema,
  type OrySession,
} from "../schemas";

export default class OryService {
  private readonly baseUrl: string;

  constructor(baseUrl?: string) {
    this.baseUrl = baseUrl ?? "";
  }

  private makeRequest<TData>(
    resource: string,
    options: {
      method?: "GET" | "POST" | "PUT" | "PATCH" | "DELETE";
      cookies?: { name: string; value: string }[];
      queryParams?: Record<string, string | number | undefined>;
      data?: TData;
    } = {},
  ): Promise<Response> {
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
  }): Promise<{ id: string; token: string }> {
    const resp = await this.makeRequest("/self-service/login", {
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

    return { id: sessionCookie.name, token: sessionCookie.value };
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

  async getSession(session: SessionModel): Promise<OrySession> {
    const resp = await this.makeRequest<OrySessionSchema>("/sessions/whoami", {
      cookies: [{ name: session.id, value: session.token }],
    });

    if (resp.status !== 200) {
      throw new Error("Unauthorized");
    }

    return orySessionParser.toModel(await resp.json());
  }
}
