import type { Translator } from "$lib/i18n";
import type { CountryModel } from "$lib/models/location";
import { ensureDefined } from "$lib/utils/array";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";

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

export function formatPlace(place?: MobileSchemas.Place): string {
  if (!place) {
    return "";
  }

  return [place.name, place.mainCity, place.country.name].filter(ensureDefined).join(", ");
}
