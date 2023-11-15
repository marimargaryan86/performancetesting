import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import { getPagination } from "../../helpers.server";
import type BeneficiaryService from "integration/junction-hub-api/services/beneficiary-service";
import type { BeneficiaryPut } from "integration/junction-hub-api/schemas/beneficiary";
import { ensureJunctionError } from "integration/common/junction-error";

function find(event: RequestEvent): ReturnType<BeneficiaryService["find"]> {
  const session = getSession(event);
  const pagination = getPagination(event);

  return integrationInstances.junctionHubApi.beneficiaries.find({ session, ...pagination });
}

function get(event: RequestEvent): ReturnType<BeneficiaryService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  return integrationInstances.junctionHubApi.beneficiaries.get({ session, id });
}

async function create(event: RequestEvent): ReturnType<BeneficiaryService["create"]> {
  const session = getSession(event);
  const data: BeneficiaryPut = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.beneficiaries.create({ session, data });
}

async function update(event: RequestEvent): ReturnType<BeneficiaryService["create"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  const data: BeneficiaryPut = devalue.parse(await event.request.text());

  return integrationInstances.junctionHubApi.beneficiaries.update({ session, id, data });
}

export async function GET(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof BeneficiaryService;

    switch (method) {
      case "find":
        return new Response(devalue.stringify(await find(event)));
      case "get":
        return new Response(devalue.stringify(await get(event)));
      default:
        throw new Error("An unexpected error occured");
    }
  } catch (err) {
    if (ensureJunctionError(err)) {
      throw error(err.status, { message: err.message });
    }

    throw error(500);
  }
}

export async function POST(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof BeneficiaryService;

    switch (method) {
      case "create":
        return new Response(devalue.stringify(await create(event)));
      case "update":
        return new Response(devalue.stringify(await update(event)));
      default:
        throw new Error("An unexpected error occured");
    }
  } catch (err) {
    if (ensureJunctionError(err)) {
      throw error(err.status, { message: err.message });
    }

    throw error(500);
  }
}
