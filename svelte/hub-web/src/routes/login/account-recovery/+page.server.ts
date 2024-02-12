import { error } from "@sveltejs/kit";
import integrationInstances from "~/integration-instances";
import type { RecoveryFlow } from "~/integration/ory/schemas/recovery-flow";
import { cookieStore } from "$lib/stores/cookie-store.server";

export async function load(event): Promise<{ flow: RecoveryFlow }> {
  const recovery = cookieStore.recoveryToken.get(event);

  let cookies: Record<string, string> | undefined;
  let flow: RecoveryFlow | undefined;

  if (recovery) {
    try {
      ({ cookies, flow } = await integrationInstances.ory.recoveryFlow.get(recovery));
    } catch {
      //
    }
  }

  if (!(cookies && flow)) {
    try {
      ({ cookies, flow } = await integrationInstances.ory.recoveryFlow.create());

      cookieStore.recoveryToken.set({ id: flow.id, cookies }, event);
    } catch {
      //
    }
  }

  if (!(cookies && flow)) {
    throw error(500);
  }

  return { flow };
}
