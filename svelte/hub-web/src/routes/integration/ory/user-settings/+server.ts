import integrationInstances from "integration-instances";
import { error } from "@sveltejs/kit";
import { cookieStore } from "stores/cookie-store.server";
import { serverServiceFactory } from "../../framework";
import userSettingsService from "./user-settings-service";

const factory = serverServiceFactory(userSettingsService);

export const POST = factory({
  async complete(event, data) {
    const session = event.locals.session;
    const userSettings = cookieStore.userSettingsToken.get(event);

    if (!userSettings) {
      throw error(400);
    }

    try {
      const flow = await integrationInstances.ory.settingsFlow.complete({
        ...userSettings,
        session,
        data,
      });

      if (event.locals.user) {
        // Update session meta if the settings update is not part of recovery flow
        cookieStore.sessionMetaToken.set(
          await integrationInstances.ory.auth.getLoggedInUser({ session }),
          event,
        );
      }

      return flow;
    } catch (err) {
      throw error(400);
    }
  },
});
