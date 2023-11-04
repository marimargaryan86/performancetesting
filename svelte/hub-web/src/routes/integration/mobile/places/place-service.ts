import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { MOBILE_INTEGRATION_ROOT } from "../common";
import type PlaceService from "integration/junction-mobile-api/services/place-service";

const ROOT = `${MOBILE_INTEGRATION_ROOT}/places`;

async function find(query: string): ReturnType<PlaceService["find"]> {
  if (query.length < 3) {
    return [];
  }

  const url = new URLExtended(ROOT, {
    base: origin,
    query: { query, action: "find" },
  });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<PlaceService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Place not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
};
