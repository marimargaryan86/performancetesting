import type { User } from "integration/ory/schemas/authentication";
import { ORY_INTEGRATION_ROOT } from "../common";
import * as devalue from "devalue";

export const ROOT = `${ORY_INTEGRATION_ROOT}/auth`;

async function login({
  id,
  data,
  rememberMe,
}: {
  id: string;
  data: Record<string, unknown>;
  rememberMe?: boolean;
}): Promise<User> {
  const resp = await fetch(new URL(ROOT, origin), {
    method: "POST",
    body: devalue.stringify({ id, data, rememberMe }),
  });

  if (resp.status !== 200) {
    throw new Error("Unauthorized");
  }

  return devalue.parse(await resp.text());
}

async function logout(): Promise<void> {
  await fetch(new URL(ROOT, origin), { method: "DELETE" });
}

export default {
  login,
  logout,
};
