import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";
import type TransactionService from "integration/junction-hub-api/services/transaction-service";

const ROOT = `${HUB_INTEGRATION_ROOT}/transactions`;

async function find({
  cursor,
  limit,
}: {
  cursor?: string;
  limit?: number;
}): ReturnType<TransactionService["find"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { cursor, limit, action: "find" } });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<TransactionService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
};
