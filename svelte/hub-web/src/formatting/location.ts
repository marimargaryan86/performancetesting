import type { LocaleData } from "i18n";
import type { CountryModel } from "models/location";

export function formatCountryOption(
  lang: LocaleData,
  option?: CountryModel,
  selected?: boolean,
): string | undefined {
  if (selected) {
    return option?.name;
  }

  return option?.name ?? lang.words.none;
}

export function formatCountryPhoneOption(
  lang: LocaleData,
  option?: CountryModel,
  selected?: boolean,
): string | undefined {
  if (selected) {
    return option?.phoneCode ? `+${option.phoneCode}` : undefined;
  }

  return option?.phoneCode ? `${option.name} (+${option.phoneCode})` : lang.words.none;
}
