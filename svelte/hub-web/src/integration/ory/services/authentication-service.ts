import {
  oryKratosIdentityParser,
  type AuthenticationSchema,
  type User,
  type Session,
} from "../schemas/authentication";
import OryService from "./ory-service";

export default class AuthenticationService extends OryService {
  async logout({ session }: { session: Session }): Promise<void> {
    const resp = await this.makeRequest<{ logout_token: string; logout_url: string }>(
      "/self-service/logout/browser",
      {
        cookies: { [session.id]: session.token },
      },
    );

    await this.makeRequest("/self-service/logout", {
      cookies: { [session.id]: session.token },
      queryParams: { token: resp.json.logout_token },
    });
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
