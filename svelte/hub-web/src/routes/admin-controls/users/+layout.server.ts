import { error } from "@sveltejs/kit";
import { permitted } from "$lib/utils/permissions";

export function load(event): void {
  const user = event.locals.user;

  if (!user || !permitted(user, "users.view")) {
    throw error(401);
  }
}
