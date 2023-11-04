import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";
import type CurrencyService from "integration/junction-hub-api/services/currency-service";

const ROOT = `${HUB_INTEGRATION_ROOT}/currencies`;

async function find({
  cursor,
  limit,
}: {
  cursor?: string;
  limit?: number;
}): ReturnType<CurrencyService["find"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { cursor, limit, action: "find" } });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

export default {
  find,
};
