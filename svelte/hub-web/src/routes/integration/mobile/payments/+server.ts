import integrationInstances from "integration-instances";
import { getSession } from "utils/auth";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type PaymentService from "integration/junction-mobile-api/services/payment-service";
import type { Price } from "integration/common/schemas/price";

async function create(event: RequestEvent): ReturnType<PaymentService["create"]> {
  const session = getSession(event);
  const data: Price = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.payments.create({ session, data });
}

export async function POST(event): Promise<Response> {
  const method = event.url.searchParams.get("action")?.toString() as keyof PaymentService;

  switch (method) {
    case "create":
      return new Response(devalue.stringify(await create(event)));
    default:
      throw error(405);
  }
}
