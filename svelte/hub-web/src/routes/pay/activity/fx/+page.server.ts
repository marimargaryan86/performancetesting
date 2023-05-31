import integrationInstances from "integration-instances";
import type { PaginatedData } from "models/common";
import type { ConversionModel } from "models/conversion";
import { getToken } from "utils/auth";

export function load(event): {
  conversions: Promise<PaginatedData<ConversionModel>>;
} {
  return {
    conversions: integrationInstances.junctionPay.conversions.listConversions(getToken(event)),
  };
}
