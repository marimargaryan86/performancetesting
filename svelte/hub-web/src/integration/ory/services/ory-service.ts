import { getCookiesFromHeaders, type Cookie } from "utils/cookies";
import { URLExtended } from "utils/url";
import type { SessionModelExtended } from "models/user";
import {
  loginFormParser,
  type LoginForm,
  type LoginFormSchema,
  type OrySessionSchema,
} from "../schemas";
import type UserService from "integration/junction-hub-api/services/user-service";

export default class OryService {
  private readonly baseUrl: string;
  private readonly userService: UserService;

  constructor(userService: UserService, baseUrl?: string) {
    this.baseUrl = baseUrl ?? "";
    this.userService = userService;
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
  }): Promise<SessionModelExtended> {
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

    const respData = (await resp.json()) as { session: OrySessionSchema };
    const permissions = await this.userService.getOwnPermissions({
      session: { id: sessionCookie.name, token: sessionCookie.value },
    });

    return {
      id: sessionCookie.name,
      token: sessionCookie.value,
      expiresAt: new Date(respData.session.expires_at),
      user: {
        id: respData.session.identity.id,
        email: respData.session.identity.traits.email,
        name: "Unknown",
        ...permissions,
      },
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
