import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";
import type JourneyService from "integration/junction-hub-api/services/journey-service";

const ROOT = `${HUB_INTEGRATION_ROOT}/journeys`;

async function find({
  cursor,
  limit,
}: {
  cursor?: string;
  limit?: number;
}): ReturnType<JourneyService["find"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { cursor, limit, action: "find" } });
  const resp = await fetch(url);

  return devalue.parse(await resp.text());
}

export default {
  find,
};
