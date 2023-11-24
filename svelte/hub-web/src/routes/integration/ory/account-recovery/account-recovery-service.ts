import type { RecoveryFlow } from "integration/ory/schemas/recovery-flow";
import { ORY_INTEGRATION_ROOT } from "../common";
import * as devalue from "devalue";

export const ROOT = `${ORY_INTEGRATION_ROOT}/account-recovery`;

async function complete(
  data: Record<string, unknown>,
): Promise<{ completed: false; flow: RecoveryFlow } | { completed: true }> {
  const resp = await fetch(new URL(ROOT, origin), {
    method: "POST",
    body: devalue.stringify(data),
  });

  if (resp.status === 200) {
    return { completed: false, flow: devalue.parse(await resp.text()) };
  }

  if (resp.status === 204) {
    return { completed: true };
  }

  throw new Error("An unexpected error occurred");
}

export default {
  complete,
};
