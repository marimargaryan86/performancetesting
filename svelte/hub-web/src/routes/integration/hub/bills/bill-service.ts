import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import type BillService from "integration/junction-hub-api/services/bill-service";
import type { Bill } from "integration/junction-hub-api/schemas/bill";
import { HUB_INTEGRATION_ROOT } from "../common";

const ROOT = `${HUB_INTEGRATION_ROOT}/bills`;

async function find({
  limit,
  cursor,
  filter,
}: {
  limit?: number;
  cursor?: string;
  filter?: Parameters<BillService["find"]>[0]["filter"];
}): ReturnType<BillService["find"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { limit, cursor, orderIds: filter?.orderIds?.join(","), action: "find" },
  });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<BillService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Bill not found");
  }

  return devalue.parse(await resp.text());
}

async function toggleReconciliation({
  bill,
}: {
  bill: Bill;
}): ReturnType<BillService["toggleReconciliation"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { action: "toggleReconciliation" } });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(bill) });

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
  toggleReconciliation,
};
