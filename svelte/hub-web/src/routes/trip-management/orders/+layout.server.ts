import { error } from "@sveltejs/kit";
import { permitted } from "utils/permissions";

export function load(event): void {
  const user = event.locals.user;

  if (!user || !permitted(user, "journey.view")) {
    throw error(401);
  }
}
