import { deleteSession, setSession } from "utils/auth";
import * as devalue from "devalue";
import integrationInstances from "integration-instances";
import jwt from "jsonwebtoken";
import { dev } from "$app/environment";
import { error } from "@sveltejs/kit";

export async function POST(event): Promise<Response> {
  const data: {
    id: string;
    data: Record<string, string>;
    rememberMe?: boolean;
  } = devalue.parse(await event.request.text());

  try {
    const { user, expiresAt, cookies } = await integrationInstances.ory.auth.login({
      ...data,
      cookies: jwt.decode(event.cookies.get("login-token") ?? "") as Record<string, string>,
    });

    const sessionCookie = Object.entries(cookies).find(([key]) => key.startsWith("ory_session"));

    if (!sessionCookie) {
      throw error(401);
    }

    setSession({
      session: {
        id: sessionCookie[0],
        token: sessionCookie[1],
        expiresAt,
        user,
      },
      rememberMe: data.rememberMe,
      event,
    });

    event.cookies.delete("login-token", { path: "/", httpOnly: true, secure: !dev });

    return new Response(devalue.stringify(user));
  } catch (err) {
    if (err instanceof Error && err.message === "2FA_REQUIRED") {
      throw error(401, { message: "2FA Required" });
    }
  }

  throw error(401);
}

export function DELETE(event): Response {
  deleteSession(event);

  return new Response(undefined, { status: 204 });
}
