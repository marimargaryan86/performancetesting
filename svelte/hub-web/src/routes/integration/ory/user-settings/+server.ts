import * as devalue from "devalue";
import integrationInstances from "integration-instances";
import { error } from "@sveltejs/kit";
import { cookieStore } from "stores/cookie-store.server";

export async function POST(event): Promise<Response> {
  const session = event.locals.session;
  const data: Record<string, string> = devalue.parse(await event.request.text());
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

    cookieStore.sessionMetaToken.set(
      await integrationInstances.ory.auth.getLoggedInUser({ session }),
      event,
    );

    return new Response(devalue.stringify(flow));
  } catch {
    throw error(400);
  }
}
