import type RefundService from "integration/junction-hub-api/services/refund-service";
import { HUB_INTEGRATION_ROOT } from "../common";
import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import type { RefundPut } from "integration/junction-hub-api/schemas/refund";

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

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<RefundService["get"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { id, action: "get" },
  });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

async function create({ data }: { data: RefundPut }): ReturnType<RefundService["create"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { action: "create" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

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

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
  create,
  update,
};
