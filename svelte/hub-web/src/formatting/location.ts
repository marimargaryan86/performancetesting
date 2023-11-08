import type { CountryModel } from "models/location";

export function formatCountryOption(option?: CountryModel, selected?: boolean): string | undefined {
  if (selected) {
    return option?.name;
  }

  return option?.name ?? "None";
}

export function formatCountryPhoneOption(
  option?: CountryModel,
  selected?: boolean,
): string | undefined {
  if (selected) {
    return option?.phoneCode ? `+${option.phoneCode}` : undefined;
  }

  return option?.phoneCode ? `${option.name} (+${option.phoneCode})` : "None";
}
