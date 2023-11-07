import type { UserPermissions } from "integration/junction-hub-api/schemas/user";

export type SessionModel = {
  id: string;
  token: string;
};

export type UserModel = {
  id: string;
  email: string;
  name: string;
} & UserPermissions;

export type SessionModelExtended = SessionModel & {
  user: UserModel;
  expiresAt: Date;
};
