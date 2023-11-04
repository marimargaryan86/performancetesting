import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";
import type { CancellationRequestCreate } from "integration/junction-hub-api/schemas/cancellation";
import type CancellationRequestService from "integration/junction-hub-api/services/cancellation-request-service";

const ROOT = `${HUB_INTEGRATION_ROOT}/cancellation-requests`;

async function create({
  data,
}: {
  data: CancellationRequestCreate;
}): ReturnType<CancellationRequestService["create"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { action: "create" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  return devalue.parse(await resp.text());
}

export default {
  create,
};
