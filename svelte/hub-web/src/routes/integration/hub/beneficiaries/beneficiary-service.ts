import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import type BeneficiaryService from "integration/junction-hub-api/services/beneficiary-service";
import type { BeneficiaryPut } from "integration/junction-hub-api/schemas/beneficiary";
import { HUB_INTEGRATION_ROOT } from "../common";

const ROOT = `${HUB_INTEGRATION_ROOT}/beneficiaries`;

async function find({
  limit,
  cursor,
}: {
  limit?: number;
  cursor?: string;
}): ReturnType<BeneficiaryService["find"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { limit, cursor, action: "find" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function get({ id }: { id: string }): ReturnType<BeneficiaryService["get"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "get" } });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Beneficiary not found");
  }

  return devalue.parse(await resp.text());
}

async function create({
  data,
}: {
  data: BeneficiaryPut;
}): ReturnType<BeneficiaryService["create"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { action: "create" } });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function update({
  data,
  id,
}: {
  id: string;
  data: BeneficiaryPut;
}): ReturnType<BeneficiaryService["update"]> {
  const url = new URLExtended(ROOT, { base: origin, query: { id, action: "update" } });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status !== 200) {
    throw new Error("Beneficiary not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  find,
  get,
  create,
  update,
};
