import { INTEGRATION_ROOT } from "../common";
import * as devalue from "devalue";

export const AUTH_ROOT = `${INTEGRATION_ROOT}/auth`;

async function signIn(data: {
  id: string;
  data: Record<string, string>;
  rememberMe: boolean;
}): Promise<boolean> {
  const url = new URL(AUTH_ROOT, origin);
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status === 200) {
    return true;
  }

  return false;
}

async function signOut(): Promise<void> {
  const url = new URL(AUTH_ROOT, origin);
  await fetch(url, { method: "DELETE" });
}

export default {
  signIn,
  signOut,
};
