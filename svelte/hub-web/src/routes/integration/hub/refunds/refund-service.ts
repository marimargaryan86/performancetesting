import type RefundService from "integration/junction-hub-api/services/refund-service";
import { HUB_INTEGRATION_ROOT } from "../common";
import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import type { RefundPositionCreate, RefundPut } from "integration/junction-hub-api/schemas/refund";

const ROOT = `${HUB_INTEGRATION_ROOT}/refunds`;

async function find({
  cursor,
  limit,
}: {
  cursor?: string;
  limit?: number;
}): ReturnType<RefundService["find"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { cursor, limit, action: "find" },
  });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<RefundService["get"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { id, action: "get" },
  });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Refund not found");
  }

  return devalue.parse(await resp.text());
}

async function update({
  id,
  data,
}: {
  id: string;
  data: RefundPut;
}): ReturnType<RefundService["update"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { id, action: "update" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function getRefundPosition({
  refundId,
  data,
}: {
  refundId: string;
  data: RefundPositionCreate;
}): ReturnType<RefundService["getRefundPosition"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { refundId, action: "getRefundPosition" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
  update,
  getRefundPosition,
};
