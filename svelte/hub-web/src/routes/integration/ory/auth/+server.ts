import integrationInstances from "integration-instances";
import { cookieStore } from "stores/cookie-store.server";
import { serverServiceFactory } from "../../framework";
import authService from "./auth-service";

// Two weeks, as set by the Legal team. Do not modify.
const EXPIRY_MAX_AGE = 1209600;

const factory = serverServiceFactory(authService);

export const POST = factory({
  async login(event, { data, rememberMe }) {
    const login = cookieStore.loginToken.get(event);

    if (!login) {
      throw new Error("Bad request");
    }

    try {
      const result = await integrationInstances.ory.loginFlow.complete({
        ...login,
        data,
      });

      if (result.state === "success") {
        const { user, expiresAt, cookies } = result;
        const sessionCookie = Object.entries(cookies).find(([key]) =>
          key.startsWith("ory_session"),
        );

        if (!sessionCookie) {
          throw new Error("Unauthorized");
        }

        const cookieOpts = { maxAge: rememberMe ? EXPIRY_MAX_AGE : undefined };

        cookieStore.sessionToken.set(
          { id: sessionCookie[0], token: sessionCookie[1] },
          event,
          cookieOpts,
        );
        cookieStore.sessionMetaToken.set({ user, expiresAt }, event, cookieOpts);
        cookieStore.loginToken.delete(event);
      } else if (result.state === "2fa") {
        cookieStore.loginToken.set({ id: result.flow.id, cookies: result.cookies }, event);
      }

      return result;
    } catch {
      throw new Error("Unauthorized");
    }
  },
  async logout(event) {
    await integrationInstances.ory.auth.logout({ session: event.locals.session });
    cookieStore.sessionToken.delete(event);
  },
  resetLogin(event) {
    cookieStore.loginToken.delete(event);

    return new Promise((r) => r());
  },
});
