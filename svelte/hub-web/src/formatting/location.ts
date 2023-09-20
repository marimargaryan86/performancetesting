import type { CountryModel } from "models/location";

export function formatCountryOption(option?: CountryModel): string {
  return option?.name ?? "None";
}

export function formatCountryPhoneOption(option?: CountryModel, selected?: boolean): string {
  if (selected && option?.phoneCode) {
    return `+${option.phoneCode}`;
  }

  return option?.phoneCode ? `${option.name} (+${option.phoneCode})` : "None";
}
