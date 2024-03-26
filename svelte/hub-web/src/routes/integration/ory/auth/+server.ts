import integrationInstances from "~/integration-instances";
import { cookieStore } from "$lib/stores/cookie-store.server";
import { server } from "./auth-service";
import type { RequestEvent } from "./$types";
import type LoginFlowService from "~/integration/ory/services/login-flow-service";

// Two weeks, as set by the Legal team. Do not modify.
const EXPIRY_MAX_AGE = 1209600;

async function loginFunc(
  event: RequestEvent,
  { data, rememberMe }: { data: Record<string, string>; rememberMe?: boolean },
): ReturnType<LoginFlowService["complete"]> {
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
      const sessionCookie = Object.entries(cookies).find(([key]) => key.startsWith("ory_session"));

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
}

export const POST = server({
  login: loginFunc,
  async logout(event) {
    await integrationInstances.ory.auth.logout({ session: event.locals.session });
    cookieStore.sessionToken.delete(event);
  },
  resetLogin(event) {
    cookieStore.loginToken.delete(event);
  },
  async directLogin(event, { username, password }) {
    const { cookies, flow } = await integrationInstances.ory.loginFlow.create();
    cookieStore.loginToken.set({ id: flow.id, cookies }, event);

    const data: Record<string, string> = {
      identifier: username,
      password,
    };

    Object.values(flow.ui.groups)
      .flat()
      .forEach((node) => {
        if (node.type === "input" && node.attributes.value) {
          if (node.attributes.name === "csrf_token") {
            // eslint-disable-next-line camelcase
            data.csrf_token = node.attributes.value;
          } else if (node.attributes.name === "method") {
            data.method = node.attributes.value;
          }
        }
      });

    const result = await loginFunc(event, { data });

    if (result.state !== "success") {
      throw new Error("Unauthorized");
    }
  },
});
