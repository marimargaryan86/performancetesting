import type { Locale, Translator } from "$lib/i18n";
import objectExt from "$lib/object-ext";
import { z } from "zod";
import type * as CommonSchemas from "~/integration/common/schemas";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type { Require } from "~/integration/ts-helpers";

export const PASSENGER_GENDERS: CommonSchemas.Gender[] = ["unspecified", "male", "female"];
export const TRAVELER_DOCUMENT_TYPES: CommonSchemas.TravelerDocumentType[] = ["passport"];

export type PartialPassengerData = Omit<Partial<MobileSchemas.OrderPassenger>, "document"> & {
  document?: Require<Partial<MobileSchemas.TravelerDocument>, "countryCodes">;
} & (
    | {
        type: "adult";
      }
    | {
        type: Exclude<PassengerType, "adult">;
        age: number;
      }
  );

export function formatTitleOption(
  translator: Translator,
  option?: CommonSchemas.PassengerTitle,
): string {
  return option ? translator(`passengerTitle.${option}`) : "";
}

export function formatGenderOption(translator: Translator, option?: CommonSchemas.Gender): string {
  return option ? translator(`gender.${option}`) : "";
}

export function formatTravelerDocumentOption(
  translator: Translator,
  option?: CommonSchemas.TravelerDocumentType,
): string {
  return option ? translator(`documentTypes.${option}`) : translator("words.none");
}

export function getPassengerTitles(locale: Locale): CommonSchemas.PassengerTitle[] {
  const base: CommonSchemas.PassengerTitle[] = ["unspecified", "mr", "mrs", "miss"];

  if (locale === "es-ES") {
    return base;
  }

  // Only add ms for English locale
  return [...base, "ms"];
}

export const MAX_TOTAL_COUNT = 9;
export const PASSENGER_DEFINITIONS = {
  senior: { from: 60, to: undefined },
  adult: { from: 28, to: 59 },
  youth: { from: 0, to: 27 },
} as const satisfies Record<PassengerType, { from: number; to?: number }>;

export function getPassengerAgeSpan(type: PassengerType): string {
  const def = PASSENGER_DEFINITIONS[type];

  return `(${def.from}${def.to === undefined ? "+" : `-${def.to}`})`;
}

export function getPassengerFullLabel(
  type: PassengerType,
  translator: Translator,
  count = 1,
): string {
  return `${translator(`passengerTypes.${type}`, { count })} ${getPassengerAgeSpan(type)}`;
}

export const PASSENGER_TYPES = ["adult", "youth", "senior"] as const;
export type PassengerType = (typeof PASSENGER_TYPES)[number];
export const passengerPickerData = z
  .array(
    z.discriminatedUnion("type", [
      z.object({ type: z.literal("adult"), age: z.undefined().optional() }),
      z.object({
        type: z.literal("youth"),
        age: z.number().min(PASSENGER_DEFINITIONS.youth.from).max(PASSENGER_DEFINITIONS.youth.to),
      }),
      z.object({
        type: z.literal("senior"),
        age: z.number().min(PASSENGER_DEFINITIONS.senior.from),
      }),
    ]),
  )
  .min(1, { message: "At least one passenger is mandatory" });

export type PassengerPickerData = z.infer<typeof passengerPickerData>;
export type PassengerEntry = PassengerPickerData[number];

export function getPassengersPresentation(
  passengers: PassengerPickerData,
  translator: Translator,
): string {
  const mapping = passengers.reduce<Partial<Record<PassengerType, number>>>(
    (prev, curr) => ({ ...prev, [curr.type]: (prev[curr.type] ?? 0) + 1 }),
    {},
  );

  return objectExt
    .entries(mapping)
    .filter((item): item is [PassengerType, number] => Boolean(item[1]))
    .map(([type, count]) => `${count} ${translator(`passengerTypes.${type}`, { count })}`)
    .join(", ");
}

export function getDefaultValue(): PassengerPickerData {
  return [{ type: "adult" }];
}
