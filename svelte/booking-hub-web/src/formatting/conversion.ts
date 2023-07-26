import { conversionStatusMapping, type ConversionStatus } from "models/conversion";

export function formatConversionStatus(status: ConversionStatus): string {
  return conversionStatusMapping[status];
}
