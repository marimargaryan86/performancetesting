import integrationInstances from "integration-instances";
import type { ConversionModel } from "models/conversion";
import { getToken } from "utils/auth";
import type { PageServerLoadEvent } from "./$types";

export async function load(
  event: PageServerLoadEvent,
): Promise<{ conversions: ConversionModel[]; conversionsCursor?: string }> {
  const [conversions, conversionsCursor] =
    await integrationInstances.junctionPay.conversions.listConversions(getToken(event));

  return {
    conversions,
    conversionsCursor,
  };
}
