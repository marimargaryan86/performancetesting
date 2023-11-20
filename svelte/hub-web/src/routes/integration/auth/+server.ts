import integrationInstances from "integration-instances";
import * as devalue from "devalue";
import { deleteSession, setSession } from "utils/auth";
import { error } from "@sveltejs/kit";

export async function POST(event): Promise<Response> {
  const data: {
    id: string;
    data: Record<string, string>;
    rememberMe: boolean;
  } = devalue.parse(await event.request.text());
  try {
    const session = await integrationInstances.ory.authenticate({
      cookies: event.cookies.getAll(),
      data: data.data,
      flowId: data.id,
    });

    setSession({
      session,
      rememberMe: data.rememberMe,
      event,
    });

    return new Response(devalue.stringify(session.user));
  } catch {
    throw error(401);
  }
}

export function DELETE(event): Response {
  deleteSession(event);

  return new Response();
}
