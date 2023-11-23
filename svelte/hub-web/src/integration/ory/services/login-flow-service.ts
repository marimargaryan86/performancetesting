import { getCookiesFromHeaders } from "utils/cookies";
import type { AuthenticatorAssurenceLevel } from "../schemas/common";
import { loginFlowParser, type LoginFlow, type LoginFlowSchema } from "../schemas/login-flow";
import OryService from "./ory-service";

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
      const cookies = getCookiesFromHeaders(resp.headers);

      return {
        flow: loginFlowParser.toModel(resp.json),
        cookies: Object.fromEntries(cookies.map(({ name, value }) => [name, value])),
      };
    }

    throw new Error("An unexpected error occurred");
  }
}
