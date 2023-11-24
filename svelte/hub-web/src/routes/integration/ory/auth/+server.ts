import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import integrationInstances from "integration-instances";
import { cookieStore } from "stores/cookie-store.server";

// Two weeks, as set by the Legal team. Do not modify.
const EXPIRY_MAX_AGE = 1209600;

export async function POST(event): Promise<Response> {
  const data: {
    id: string;
    data: Record<string, string>;
    rememberMe?: boolean;
  } = devalue.parse(await event.request.text());

  try {
    const { user, expiresAt, cookies } = await integrationInstances.ory.auth.login({
      ...data,
      cookies: cookieStore.loginToken.get(event) ?? {},
    });

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

    return new Response(devalue.stringify(user));
  } catch (err) {
    if (err instanceof Error && err.message === "2FA_REQUIRED") {
      throw error(401, { message: "2FA Required" });
    }
  }

  throw error(401);
}

export function DELETE(event): Response {
  cookieStore.sessionToken.delete(event);

  return new Response(undefined, { status: 204 });
}
