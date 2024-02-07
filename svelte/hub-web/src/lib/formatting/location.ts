import type { Translator } from "~/i18n";
import type { CountryModel } from "~/models/location";

export function formatCountryOption(
  translator: Translator,
  option?: CountryModel,
  selected?: boolean,
): string | undefined {
  if (selected) {
    return option?.name;
  }

  return option?.name ?? translator("words.none");
}

export function formatCountryPhoneOption(
  translator: Translator,
  option?: CountryModel,
  selected?: boolean,
): string | undefined {
  if (selected) {
    return option?.phoneCode ? `+${option.phoneCode}` : undefined;
  }

  return option?.phoneCode ? `${option.name} (+${option.phoneCode})` : translator("words.none");
}
