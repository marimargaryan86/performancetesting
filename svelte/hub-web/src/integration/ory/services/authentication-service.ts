import { getCookiesFromHeaders } from "utils/cookies";
import {
  oryKratosIdentityParser,
  type AuthenticationSchema,
  type User,
  type Session,
} from "../schemas/authentication";
import OryService from "./ory-service";

export default class AuthenticationService extends OryService {
  async login({
    id,
    data,
    cookies,
  }: {
    id: string;
    data: Record<string, string>;
    cookies: Record<string, string>;
  }): Promise<{
    user: User;
    expiresAt: Date;
    cookies: Record<string, string>;
  }> {
    const resp = await this.makeRequest<AuthenticationSchema>("/self-service/login", {
      method: "POST",
      queryParams: { flow: id },
      cookies,
      data,
    });

    if (resp.status === 422) {
      throw new Error("2FA_REQUIRED");
    }

    if (resp.status !== 200) {
      throw new Error("UNAUTHORIZED");
    }

    return {
      user: oryKratosIdentityParser.toModel(resp.json.session.identity),
      expiresAt: new Date(resp.json.session.expires_at),
      cookies: Object.fromEntries(
        getCookiesFromHeaders(resp.headers).map(({ name, value }) => [name, value]),
      ),
    };
  }

  async getLoggedInUser({ session }: { session: Session }): Promise<{
    user: User;
    expiresAt: Date;
  }> {
    const resp = await this.makeRequest<AuthenticationSchema["session"]>("/sessions/whoami", {
      cookies: { [session.id]: session.token },
    });

    if (resp.status === 200) {
      return {
        user: oryKratosIdentityParser.toModel(resp.json.identity),
        expiresAt: new Date(resp.json.expires_at),
      };
    }

    throw new Error("UNAUTHORIZED");
  }
}
