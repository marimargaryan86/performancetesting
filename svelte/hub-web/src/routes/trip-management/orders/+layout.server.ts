import { error } from "@sveltejs/kit";
import { getSession } from "utils/auth";
import { permitted } from "utils/permissions";

export function load(event): void {
  const session = getSession(event);

  if (!permitted(session.user, "journey", "view")) {
    throw error(401);
  }
}
