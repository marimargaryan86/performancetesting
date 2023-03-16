import type { ServerLoadEvent } from "@sveltejs/kit";
import type { UserJwtSchema } from "integration/schemas/user";
import jwtDecode from "jwt-decode";
import type { UserModel } from "models/user";

export function load(event: ServerLoadEvent): { user?: UserModel } {
  const token = event.cookies.get("session-token");

  try {
    const user: UserJwtSchema | undefined = token ? jwtDecode(token) : undefined;

    if (user) {
      return { user: { email: user.user_info.email, id: user.user_info.id, name: "John Smith" } };
    }
  } catch {
    //
  }

  return {};
}
