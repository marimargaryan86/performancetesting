import { getCookiesFromHeaders } from "$lib/utils/cookies";
import type { AuthenticatorAssurenceLevel } from "../schemas/common";
import { loginFlowParser, type LoginFlow, type LoginFlowSchema } from "../schemas/login-flow";
import OryService from "./ory-service";
import {
  oryKratosIdentityParser,
  type AuthenticationSchema,
  type User,
} from "../schemas/authentication";

export default class LoginFlowService extends OryService {
  async create(
    opts: {
      cookies?: Record<string, string>;
      refresh?: boolean;
      aal?: AuthenticatorAssurenceLevel;
      returnTo?: string;
      loginChallenge?: string;
      organization?: string;
    } = {},
  ): Promise<{
    flow: LoginFlow;
    cookies: Record<string, string>;
  }> {
    const resp = await this.makeRequest<LoginFlowSchema>("/self-service/login/browser", {
      queryParams: {
        refresh: opts.refresh ? String(opts.refresh) : undefined,
        aal: opts.aal,
        /* eslint-disable camelcase */
        return_to: opts.returnTo,
        login_challenge: opts.loginChallenge,
        /* eslint-enable camelcase */
        organization: opts.organization,
      },
      cookies: opts.cookies,
    });

    if (resp.status === 200) {
      return {
        flow: loginFlowParser.toModel(resp.json),
        cookies: Object.fromEntries(
          getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
        ),
      };
    }

    throw new Error("An unexpected error occurred");
  }

  async get({
    id,
    cookies,
  }: {
    id: string;
    cookies: Record<string, string>;
  }): Promise<{ cookies: Record<string, string>; flow: LoginFlow }> {
    const resp = await this.makeRequest<LoginFlowSchema>("/self-service/login/flows", {
      queryParams: { id },
      cookies,
    });

    if (resp.status !== 200) {
      throw new Error("An unexpected error occurred");
    }

    return {
      cookies: Object.fromEntries(
        getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
      ),
      flow: loginFlowParser.toModel(resp.json),
    };
  }

  async complete({
    id,
    cookies,
    data,
  }: {
    id: string;
    cookies: Record<string, string>;
    data: Record<string, string>;
  }): Promise<
    | { state: "success"; user: User; expiresAt: Date; cookies: Record<string, string> }
    | { state: "2fa"; flow: LoginFlow; cookies: Record<string, string> }
    | { state: "fail"; flow: LoginFlow }
  > {
    const resp = await this.makeRequest("/self-service/login", {
      queryParams: { flow: id },
      cookies,
      data,
      method: "POST",
    });

    const respCookies = Object.fromEntries(
      getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
    );

    if (resp.status === 200) {
      const jsonData = resp.json as AuthenticationSchema;

      return {
        state: "success",
        user: oryKratosIdentityParser.toModel(jsonData.session.identity),
        expiresAt: new Date(jsonData.session.expires_at),
        cookies: respCookies,
      };
    }

    if (resp.status === 422) {
      const nextFlow = await this.create({ aal: "aal2", cookies: respCookies });

      return {
        state: "2fa",
        flow: nextFlow.flow,
        cookies: { ...respCookies, ...nextFlow.cookies },
      };
    }

    try {
      return {
        state: "fail",
        flow: loginFlowParser.toModel(resp.json as LoginFlowSchema),
      };
    } catch {
      throw new Error("An unexpected error occurred");
    }
  }
}
