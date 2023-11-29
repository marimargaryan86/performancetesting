import { ORY_INTEGRATION_ROOT } from "../common";
import * as devalue from "devalue";
import type { SettingsFlow } from "integration/ory/schemas/settings-flow";

export const ROOT = `${ORY_INTEGRATION_ROOT}/user-settings`;

async function complete(data: Record<string, unknown>): Promise<SettingsFlow> {
  const resp = await fetch(new URL(ROOT, origin), {
    method: "POST",
    body: devalue.stringify(data),
  });

  if (resp.status === 200) {
    return devalue.parse(await resp.text());
  }

  throw new Error("An unexpected error occurred");
}

export default {
  complete,
};
