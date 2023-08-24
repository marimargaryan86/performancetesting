import type { CountryModel } from "models/location";

export function formatCountryOption(option?: CountryModel): string {
  return option?.name ?? "None";
}
