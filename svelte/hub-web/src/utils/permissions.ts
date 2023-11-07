import type { UserPermissions } from "integration/junction-hub-api/schemas/user";
import type { UserModel } from "models/user";

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

export type PermissionAction = Exclude<
  {
    [key in keyof UserPermissions["permissions"]]: key extends `${string}.${infer action}`
      ? action
      : never;
  }[keyof UserPermissions["permissions"]],
  undefined
>;

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
