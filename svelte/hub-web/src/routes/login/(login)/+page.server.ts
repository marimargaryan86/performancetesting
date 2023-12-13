import { error, redirect } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { LoginFlow } from "integration/ory/schemas/login-flow";
import { cookieStore } from "stores/cookie-store.server";
import type { RequestEvent } from "./$types";
import { ROOT as ORY_AUTH_ROOT } from "../../integration/ory/auth/auth-service";
import * as devalue from "devalue";
import type { User } from "integration/ory/schemas/authentication";
import routeConfig from "routeConfig";

/**
 * Due to Grupo requirements, we need to be able to authenticate a user with
 * query parameters. We support this login flow by passing query parameters
 * `?username={user@example.com}&password={password123} to `/login`. Auth
 * is handled in the SvelteKit BE, and on successful authentication, the user is
 * redirected to the proper page (root for Snowfall admins, book for others).
 *
 * Note that this requires the password in clear text. While this is a known
 * security concern, it's unavoidable due to business requirements.
 *
 * @param event - The SvelteKit request `Event`
 * @param flow - Template `LoginFlow` for ORY
 * @returns A `LoginFlow` useable by ORY to authenticate a user and log in.
 */
async function autoLogin(event: RequestEvent, flow: LoginFlow): Promise<LoginFlow | undefined> {
  const { username, password } = Object.fromEntries(event.url.searchParams);
  const login = cookieStore.loginToken.get(event);

  if (!(login && username && password)) {
    return;
  }

  const loginData: Record<string, string> = {
    password,
    identifier: username,
  };

  Object.values(flow.ui.groups)
    .flat()
    .forEach((node) => {
      if (node.type === "input") {
        if (node.attributes.name === "identifier" || node.attributes.name === "password") {
          return;
        }

        if (node.attributes.value) {
          loginData[node.attributes.name] = node.attributes.value;
        }
      }
    });

  const loginResp = await event.fetch(ORY_AUTH_ROOT, {
    method: "POST",
    body: devalue.stringify({ data: loginData, rememberMe: false }),
  });

  if (loginResp.status !== 200) {
    return;
  }

  const data = devalue.parse(await loginResp.text()) as
    | { state: "success"; user: User }
    | { state: "fail"; flow: LoginFlow };

  if (data.state === "fail") {
    return data.flow;
  }

  const redirectUrl =
    data.user.role === "reseller-admin" || data.user.role === "reseller-user"
      ? routeConfig.routes.tripManagement.routes.book.root
      : routeConfig.root;

  throw redirect(303, redirectUrl);
}

export async function load(event): Promise<{ flow: LoginFlow }> {
  const login = cookieStore.loginToken.get(event);

  let cookies: Record<string, string> | undefined;
  let flow: LoginFlow | undefined;

  if (login) {
    try {
      ({ cookies, flow } = await integrationInstances.ory.loginFlow.get(login));
    } catch {
      //
    }
  }

  if (!(cookies && flow)) {
    try {
      ({ cookies, flow } = await integrationInstances.ory.loginFlow.create());

      cookieStore.loginToken.set({ id: flow.id, cookies }, event);
    } catch {
      //
    }
  }

  if (!(cookies && flow)) {
    throw error(500);
  }

  return { flow: (await autoLogin(event, flow)) ?? flow };
}
