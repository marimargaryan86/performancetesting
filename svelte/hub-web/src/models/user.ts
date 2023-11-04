import type { OrySession } from "integration/ory/schemas";

export interface SessionModel {
  id: string;
  token: string;
}

export type UserModel = OrySession["data"];
