import integrationInstances from "integration-instances";
import type { RequestEvent } from "./$types";
import { error } from "@sveltejs/kit";
import * as devalue from "devalue";
import type PaymentService from "integration/junction-mobile-api/services/payment-service";
import type { Price } from "integration/common/schemas/price";
import { ensureJunctionError } from "integration/common/junction-error";

async function create(event: RequestEvent): ReturnType<PaymentService["create"]> {
  const session = event.locals.session;
  const data: Price = devalue.parse(await event.request.text());

  return integrationInstances.junctionMobileApi.payments.create({ session, data });
}

export async function POST(event): Promise<Response> {
  try {
    const method = event.url.searchParams.get("action")?.toString() as keyof PaymentService;

    switch (method) {
      case "create":
        return new Response(devalue.stringify(await create(event)));
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
