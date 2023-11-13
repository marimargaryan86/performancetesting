import type AccountService from "integration/junction-hub-api/services/account-service";
import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";

const ROOT = `${HUB_INTEGRATION_ROOT}/accounts`;

async function find({
  limit,
  cursor,
}: {
  limit?: number;
  cursor?: string;
}): ReturnType<AccountService["find"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { limit, cursor, action: "find" },
  });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<AccountService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Account not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
};
