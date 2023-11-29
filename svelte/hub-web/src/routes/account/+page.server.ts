import { error } from "@sveltejs/kit";
import integrationInstances from "integration-instances";
import type { SettingsFlow } from "integration/ory/schemas/settings-flow.js";
import { cookieStore } from "stores/cookie-store.server";

export async function load(event): Promise<{ flow: SettingsFlow }> {
  const session = event.locals.session;
  const userSettings = cookieStore.userSettingsToken.get(event);

  let cookies: Record<string, string> | undefined;
  let flow: SettingsFlow | undefined;

  if (userSettings) {
    try {
      ({ cookies, flow } = await integrationInstances.ory.settingsFlow.get({
        ...userSettings,
        session,
      }));
    } catch {
      //
    }
  }

  if (!(cookies && flow)) {
    try {
      ({ cookies, flow } = await integrationInstances.ory.settingsFlow.create({ session }));

      cookieStore.userSettingsToken.set({ id: flow.id, cookies }, event);
    } catch {
      //
    }
  }

  if (!(cookies && flow)) {
    throw error(500);
  }

  return { flow };
}
