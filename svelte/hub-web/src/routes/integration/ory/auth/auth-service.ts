import { ORY_INTEGRATION_ROOT } from "../common";
import * as devalue from "devalue";
import type { User } from "integration/ory/schemas/authentication";
import type { LoginFlow } from "integration/ory/schemas/login-flow";
import { URLExtended } from "utils/url";

export const ROOT = `${ORY_INTEGRATION_ROOT}/auth`;

async function resetLogin(): Promise<void> {
  await fetch(new URLExtended(ROOT, { base: origin, query: { action: "reset" } }), {
    method: "DELETE",
  });
}

async function login({
  data,
  rememberMe,
}: {
  data: Record<string, unknown>;
  rememberMe?: boolean;
}): Promise<{ state: "success"; user: User } | { state: "fail" | "2fa"; flow: LoginFlow }> {
  const resp = await fetch(new URL(ROOT, origin), {
    method: "POST",
    body: devalue.stringify({ data, rememberMe }),
  });

  if (resp.status !== 200) {
    throw new Error("Unauthorized");
  }

  return devalue.parse(await resp.text());
}

async function logout(): Promise<void> {
  await fetch(new URLExtended(ROOT, { base: origin, query: { action: "logout" } }), {
    method: "DELETE",
  });
}

export default {
  resetLogin,
  login,
  logout,
};
