import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { HUB_INTEGRATION_ROOT } from "../common";
import type CompanyService from "integration/junction-hub-api/services/company-service";

const ROOT = `${HUB_INTEGRATION_ROOT}/companies`;

async function get({ id }: { id: string }): ReturnType<CompanyService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Company not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  get,
};
