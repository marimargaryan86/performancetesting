import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";
import type ConversionService from "integration/junction-hub-api/services/conversion-service";

const ROOT = `${HUB_INTEGRATION_ROOT}/conversions`;

async function find({
  cursor,
  limit,
}: {
  cursor?: string;
  limit?: number;
}): ReturnType<ConversionService["find"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { cursor, limit, action: "find" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<ConversionService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Conversion not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
};
