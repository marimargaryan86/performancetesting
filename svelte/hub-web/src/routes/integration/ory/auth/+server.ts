import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import integrationInstances from "integration-instances";
import { cookieStore } from "stores/cookie-store.server";

// Two weeks, as set by the Legal team. Do not modify.
const EXPIRY_MAX_AGE = 1209600;

export async function POST(event): Promise<Response> {
  const login = cookieStore.loginToken.get(event);

  if (!login) {
    throw error(400);
  }

  const data: {
    data: Record<string, string>;
    rememberMe?: boolean;
  } = devalue.parse(await event.request.text());

  try {
    const result = await integrationInstances.ory.loginFlow.complete({
      ...login,
      data: data.data,
    });

    if (result.state === "success") {
      const { user, expiresAt, cookies } = result;
      const sessionCookie = Object.entries(cookies).find(([key]) => key.startsWith("ory_session"));

      if (!sessionCookie) {
        throw error(401);
      }

      const cookieOpts = { maxAge: data.rememberMe ? EXPIRY_MAX_AGE : undefined };

      cookieStore.sessionToken.set(
        { id: sessionCookie[0], token: sessionCookie[1] },
        event,
        cookieOpts,
      );
      cookieStore.sessionMetaToken.set({ user, expiresAt }, event, cookieOpts);
      cookieStore.loginToken.delete(event);

      return new Response(devalue.stringify({ state: "success", user }));
    } else if (result.state === "fail") {
      return new Response(devalue.stringify({ state: "fail", flow: result.flow }));
    } else if (result.state === "2fa") {
      cookieStore.loginToken.set({ id: result.flow.id, cookies: result.cookies }, event);

      return new Response(devalue.stringify({ state: "2fa", flow: result.flow }));
    }
  } catch {
    //
  }

  throw error(401);
}

export async function DELETE(event): Promise<Response> {
  const action = event.url.searchParams.get("action")?.toString();

  switch (action) {
    case "logout":
      await integrationInstances.ory.auth.logout({ session: event.locals.session });
      cookieStore.sessionToken.delete(event);
      break;
    case "reset":
      cookieStore.loginToken.delete(event);
      break;
    default:
      throw error(404);
  }

  return new Response(undefined, { status: 204 });
}
