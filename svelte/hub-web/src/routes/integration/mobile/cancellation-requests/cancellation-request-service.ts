import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { MOBILE_INTEGRATION_ROOT } from "../common";
import type { CancellationRequestCreate } from "integration/junction-mobile-api/schemas/cancellation";
import type CancellationRequestService from "integration/junction-mobile-api/services/cancellation-request-service";

const ROOT = `${MOBILE_INTEGRATION_ROOT}/cancellation-requests`;

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

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<CancellationRequestService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Cancellation request not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  create,
  get,
};
