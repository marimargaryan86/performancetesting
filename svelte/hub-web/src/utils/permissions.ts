import type { UserPermissions } from "integration/junction-hub-api/schemas/user";
import type { UserModel } from "models/user";

/**
 * Represents a resource in the Junction Mobile or Hub API. Extracts the
 * `resource` part from permission strings (format: "resource.action") in
 * `UserPermissions`, including the superadmin wildcard `"*"`.
 *
 */
export type PermissionModule =
  | "*"
  | Exclude<
      {
        [key in keyof UserPermissions["permissions"]]: key extends `${infer module}.${string}`
          ? module
          : never;
      }[keyof UserPermissions["permissions"]],
      undefined
    >;

/**
 * Represents an action in the Junction Mobile or Hub API. Extracts the
 * `action` part from permission strings (format: "resource.action") in
 * `UserPermissions`, including the superadmin wildcard `"*"`.
 *
 */
export type PermissionAction = Exclude<
  {
    [key in keyof UserPermissions["permissions"]]: key extends `${string}.${infer action}`
      ? action
      : never;
  }[keyof UserPermissions["permissions"]],
  undefined
>;

/**
 * Checks if a user has the specified permission for a resource and action.
 *
 * @param {UserModel} user - The `user` object, including its `permissions`.
 * @param {PermissionModule} resource - The resource part of the permission to check.
 * @param {PermissionAction} [action] - The action part of the permission to check. Optional.
 * @returns {boolean} - `true` if the user has the specified permission, `false` otherwise.
 *
 * @example
 * permitted(user, "booking", "view") // Checks if the user has permission for "booking.view".
 * permitted(user, "booking") // Checks if the user has any permission for the "booking" resource.
 */
export function permitted(
  user: UserModel,
  module: PermissionModule,
  action?: PermissionAction,
): boolean {
  const wildCardPermission = `${module}.*`;
  const permission = `${module}${action ? `.${action}` : ""}`;

  return (
    "*" in user.permissions ||
    wildCardPermission in user.permissions ||
    permission in user.permissions
  );
}
