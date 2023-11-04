import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import type BalanceService from "integration/junction-hub-api/services/balance-service";
import type { BalanceAdd } from "integration/junction-hub-api/schemas/balance";
import { HUB_INTEGRATION_ROOT } from "../common";

const ROOT = `${HUB_INTEGRATION_ROOT}/balances`;

async function find({
  accountId,
  limit,
  cursor,
}: {
  accountId: string;
  limit?: number;
  cursor?: string;
}): ReturnType<BalanceService["find"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { limit, cursor, accountId, action: "find" },
  });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

async function create({
  accountId,
  data,
}: {
  accountId: string;
  data: BalanceAdd;
}): ReturnType<BalanceService["create"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { accountId, action: "create" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  return devalue.parse(await resp.text());
}

export default {
  find,
  create,
};
