import integrationInstances from "integration-instances";
import type { LoginFlow } from "integration/ory/schemas/login-flow";
import { cookieStore } from "stores/cookie-store.server";

export async function load(event): Promise<{ flow: LoginFlow }> {
  const { flow, cookies } = await integrationInstances.ory.loginFlow.create();

  cookieStore.loginToken.set(cookies, event);

  return { flow };
}
