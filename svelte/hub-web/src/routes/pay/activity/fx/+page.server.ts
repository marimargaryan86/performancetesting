import integrationInstances from "integration-instances";
import type { ConversionModel } from "models/conversion";
import { getToken } from "utils/auth";
import type { PageServerLoadEvent } from "./$types";

export async function load(
  event: PageServerLoadEvent,
): Promise<{ conversions: ConversionModel[] }> {
  return {
    conversions: await integrationInstances.junctionPay.conversions.listConversions(
      getToken(event),
    ),
  };
}
