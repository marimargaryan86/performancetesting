import type { CountryModel } from "models/location";

export function formatCountryOption(option?: CountryModel): string {
  return option?.name ?? "None";
}

export function formatCountryPhoneOption(option?: CountryModel): string {
  return option?.phoneCode ? `+${option.phoneCode} (${option.name})` : "None";
}
