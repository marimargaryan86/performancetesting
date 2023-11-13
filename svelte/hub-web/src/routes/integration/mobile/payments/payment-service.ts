import { URLExtended } from "utils/url";
import * as devalue from "devalue";
import { MOBILE_INTEGRATION_ROOT } from "../common";
import type PaymentService from "integration/junction-mobile-api/services/payment-service";
import type { Price } from "integration/common/schemas/price";

const ROOT = `${MOBILE_INTEGRATION_ROOT}/payments`;

async function create({ data }: { data: Price }): ReturnType<PaymentService["create"]> {
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

export default {
  create,
};
