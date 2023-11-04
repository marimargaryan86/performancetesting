import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type CompanyService from "integration/junction-hub-api/services/company-service";

function get(event: RequestEvent): ReturnType<CompanyService["get"]> {
  const session = getSession(event);
  const id = event.url.searchParams.get("id")?.toString();

  if (!id) {
    throw error(404);
  }

  try {
    return integrationInstances.junctionHubApi.companies.get({ session, id });
  } catch {
    throw error(404);
  }
}

export async function GET(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof CompanyService;

  switch (method) {
    case "get":
      return new Response(devalue.stringify(await get(event)));
    default:
      throw error(405);
  }
}
