import * as devalue from "devalue";
import integrationInstances from "integration-instances";
import { error } from "@sveltejs/kit";
import { cookieStore } from "stores/cookie-store.server";

export async function POST(event): Promise<Response> {
  const data: Record<string, string> = devalue.parse(await event.request.text());
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
      cookieStore.sessionMetaToken.set(
        await integrationInstances.ory.auth.getLoggedInUser({ session: result.session }),
        event,
      );

      return new Response(undefined, { status: 204 });
    }

    return new Response(devalue.stringify(result.flow));
  } catch {
    cookieStore.recoveryToken.delete(event);
    throw error(400);
  }
}
