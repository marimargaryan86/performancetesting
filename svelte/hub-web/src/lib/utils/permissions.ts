import type * as OrySchemas from "~/integration/ory/schemas";
import { getContext, setContext } from "svelte";
import type { Readable, Writable } from "svelte/store";

/**
 * Base permissions, this list should be expanded upon as more permissions are created
 */
const BASE_PERMISSIONS = {
  "journey.view": 2,
  "journey.add": 2 ** 2,
  "order.view": 2 ** 3,
  "order.add": 2 ** 4,
  "booking.view": 2 ** 5,
  "booking.add": 2 ** 6,
  "cancel.view": 2 ** 7,
  "cancel.add": 2 ** 8,
  "refund.view": 2 ** 9,
  "refund.add": 2 ** 10,
  "transaction.view": 2 ** 11,
  "transaction.add": 2 ** 12,
  "user.view": 2 ** 13,
  "user.add": 2 ** 14,
  "users.view": 2 ** 15,
  "users.add": 2 ** 16,
};

const PERMISSIONS = {
  ...BASE_PERMISSIONS,
  "*": Object.values(BASE_PERMISSIONS).reduce((prev, curr) => prev | curr) | 1,
};

export type Action = keyof typeof PERMISSIONS;

/**
 * Get the number identifying a permission
 * @param actions Actions to generate the number identifier from
 * @returns A uniquely identifying number for the permission
 */
function getPermission(...actions: Action[]): number {
  return Object.entries(PERMISSIONS).reduce(
    (prev, [key, val]) => prev | (actions.includes(key as Action) ? val : 0),
    0,
  );
}

/**
 * Mapping between the user role and its permissions.
 */
const ROLE_MAPPING: Record<OrySchemas.UserRole, number> = {
  "snowfall-admin": getPermission("*"),
  "snowfall-user": getPermission(
    "journey.view",
    "order.view",
    "booking.view",
    "cancel.view",
    "cancel.add",
    "refund.view",
    "refund.add",
    "transaction.view",
    "transaction.add",
  ),
  "reseller-admin": getPermission(
    "journey.view",
    "journey.add",
    "order.view",
    "order.add",
    "booking.view",
    "booking.add",
    "cancel.view",
    "cancel.add",
    "refund.view",
    "user.view",
    "user.add",
  ),
  "reseller-user": getPermission(
    "journey.view",
    "journey.add",
    "order.view",
    "order.add",
    "booking.view",
    "booking.add",
    "cancel.view",
    "cancel.add",
    "refund.view",
  ),
};

/**
 * Check whether or not a user is permitted to perform an action
 * @param user The user in question
 * @param actions Actions that the user must be permitted to perform
 * @returns true if the user is permitted, otherwise false
 */
export function permitted(user: OrySchemas.User, ...actions: Action[]): boolean {
  const permission = getPermission(...actions);

  return (permission & ROLE_MAPPING[user.role]) === permission;
}

/**
 * Create a context for the currently signed in user
 * @param user The signed in user
 * @returns A writable store for the signed in user
 */
export function setUser(user: Writable<OrySchemas.User>): Writable<OrySchemas.User> {
  return setContext("user", user);
}

/**
 * Get the currently signed in user
 * @returns The currently signed in user
 */
export function getUser(): Readable<OrySchemas.User> {
  return getContext("user");
}
