import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";
import type TransactionService from "integration/junction-hub-api/services/transaction-service";

const ROOT = `${HUB_INTEGRATION_ROOT}/transactions`;

async function find({
  cursor,
  limit,
  sort,
  filter,
}: {
  cursor?: string;
  limit?: number;
  sort?: Parameters<TransactionService["find"]>[0]["sort"];
  filter?: Parameters<TransactionService["find"]>[0]["filter"];
}): ReturnType<TransactionService["find"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: {
      cursor,
      limit,
      action: "find",
      sort,
      ids: filter?.ids?.join(","),
      billIds: filter?.billIds?.join(","),
      externalReference: filter?.externalReference,
    },
  });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<TransactionService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Transaction not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
};
