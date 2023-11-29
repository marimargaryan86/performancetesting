import type { UserRole } from "integration/ory/schemas/authentication";
import { capitalize } from "utils/common";

export function formatRole(role: UserRole): string {
  return capitalize(role.replaceAll("-", " "));
}
