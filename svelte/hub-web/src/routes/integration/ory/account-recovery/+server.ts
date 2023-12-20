import integrationInstances from "integration-instances";
import { error } from "@sveltejs/kit";
import { cookieStore } from "stores/cookie-store.server";
import { serverServiceFactory } from "../../framework";
import accountRecoveryService from "./account-recovery-service";

const factory = serverServiceFactory(accountRecoveryService);

export const POST = factory({
  async complete(event, data) {
    const recovery = cookieStore.recoveryToken.get(event);

    if (!recovery) {
      throw error(400);
    }

    try {
      const result = await integrationInstances.ory.recoveryFlow.complete({ ...recovery, data });

      if (result.completed) {
        cookieStore.recoveryToken.delete(event);
        cookieStore.loginToken.delete(event);
        cookieStore.sessionToken.set(result.session, event);
      }

      return result;
    } catch {
      cookieStore.recoveryToken.delete(event);
      throw error(400);
    }
  },
});
