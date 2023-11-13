import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { MOBILE_INTEGRATION_ROOT } from "../common";
import type TripService from "integration/junction-mobile-api/services/trip-service";
import type { TripCandidateSearchCreate } from "integration/junction-mobile-api/schemas/trip-candidate";

const ROOT = `${MOBILE_INTEGRATION_ROOT}/trips`;

async function create({
  data,
}: {
  data: TripCandidateSearchCreate;
}): Promise<ReturnType<TripService["create"]>> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { action: "create" },
  });
  const resp = await fetch(url, { method: "POST", body: devalue.stringify(data) });

  if (resp.status !== 200) {
    throw new Error("An unexpected error occurred");
  }

  return devalue.parse(await resp.text());
}

async function findOffers({
  id,
  cursor,
  limit,
}: {
  id: string;
  cursor?: string;
  limit?: number;
}): ReturnType<TripService["findOffers"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { id, cursor, limit, action: "findOffers" },
  });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Trip candidate not found");
  }

  return devalue.parse(await resp.text());
}

async function getTripCandidateSearch({
  id,
}: {
  id: string;
}): ReturnType<TripService["getTripCandidateSearch"]> {
  const url = new URLExtended(ROOT, {
    base: origin,
    query: { id, action: "getTripCandidateSearch" },
  });
  const resp = await fetch(url);

  if (resp.status !== 200) {
    throw new Error("Trip candidate not found");
  }

  return devalue.parse(await resp.text());
}

export default {
  create,
  findOffers,
  getTripCandidateSearch,
};
