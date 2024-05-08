import { getCookieJar } from "$lib/utils/cookie-jar";
import { error } from "@sveltejs/kit";
import integrationInstancesServer from "~/integration-instances";
import type { OnboardingModel } from "~/integration/junction-hub-api/schemas/onboarding";
import { ONBOARDING_COOKIE } from "./+page.svelte";

export async function load(event): Promise<{ onboarding: OnboardingModel; completed: boolean }> {
  const token = event.url.searchParams.get("token")?.toString();

  if (!token) {
    throw error(400, { message: "Onboarding token unspecified" });
  }

  try {
    const onboarding = await integrationInstancesServer.junctionHubApi.onboarding.get(token);

    return {
      onboarding,
      completed: getCookieJar({ event }).get(ONBOARDING_COOKIE) === token,
    };
  } catch (err) {
    throw error(400, { message: "Invalid token" });
  }
}
