import integrationInstances from "~/integration-instances";
import { cookieStore } from "$lib/stores/cookie-store.server";
import { serverServiceFactory } from "../../framework";
import accountRecoveryService from "./account-recovery-service";

const factory = serverServiceFactory(accountRecoveryService);

export const POST = factory({
  async complete(event, data) {
    const recovery = cookieStore.recoveryToken.get(event);

    if (!recovery) {
      throw new Error("Bad request");
    }

    try {
      const result = await integrationInstances.ory.recoveryFlow.complete({ ...recovery, data });

      if (result.completed) {
        cookieStore.recoveryToken.delete(event);
        cookieStore.loginToken.delete(event);
        cookieStore.sessionToken.set(result.session, event);
      }

      return result;
    } catch (err) {
      cookieStore.recoveryToken.delete(event);
      throw err;
    }
  },
});
