import { error } from "@sveltejs/kit";
import { permitted } from "utils/permissions";

export function load(event): void {
  const user = event.locals.user;

  if (!user || !permitted(user, "transaction", "*")) {
    throw error(401);
  }
}
