import { error } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { LoginFlow } from "integration/ory/schemas/login-flow";
import { cookieStore } from "stores/cookie-store.server";

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

  return { flow };
}
