import type { Locale, Translator } from "$lib/i18n";
import { ensureDefined } from "$lib/utils/array";
import { z } from "zod";
import type * as CommonSchemas from "~/integration/common/schemas";
import type * as MobileSchemas from "~/integration/junction-mobile-api/schemas";
import type { Require } from "~/integration/ts-helpers";

export const PASSENGER_GENDERS: CommonSchemas.Gender[] = ["unspecified", "male", "female"];
export const TRAVELER_DOCUMENT_TYPES: CommonSchemas.TravelerDocumentType[] = ["passport"];

export type PartialPassengerData = Omit<Partial<MobileSchemas.OrderPassenger>, "document"> & {
  type: keyof PassengerPickerData;
  document?: Require<Partial<MobileSchemas.TravelerDocument>, "countryCodes">;
};

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

  if (locale === "es-ES" || locale === "sv") {
    return base;
  }

  // Only add ms for English locale
  return [...base, "ms"];
}

export type PassengerType = "senior" | "adult" | "youth" | "child";

export const MAX_TOTAL_COUNT = 9;
export const PASSENGER_DEFINITIONS: Record<
  keyof PassengerPickerData,
  { type: PassengerType; span: { from: number; to?: number } }
> = {
  seniors65: { type: "senior", span: { from: 65 } },
  seniors60: { type: "senior", span: { from: 60, to: 64 } },
  adults: { type: "adult", span: { from: 26, to: 59 } },
  youths15: { type: "youth", span: { from: 15, to: 25 } },
  youths12: { type: "youth", span: { from: 12, to: 14 } },
  children6: { type: "child", span: { from: 6, to: 11 } },
  children4: { type: "child", span: { from: 4, to: 5 } },
  children0: { type: "child", span: { from: 0, to: 3 } },
};

export function getPassengerFullLabel(
  type: keyof PassengerPickerData,
  translator: Translator,
  count = 1,
): string {
  const def = PASSENGER_DEFINITIONS[type];

  return `${translator(`passengerTypes.${def.type}`, { count })} (${def.span.from}${
    def.span.to === undefined ? "+" : `-${def.span.to}`
  })`;
}

export const passengerPickerData = z
  .object({
    seniors65: z.number().min(0),
    seniors60: z.number().min(0),
    adults: z.number().min(0),
    youths15: z.number().min(0),
    youths12: z.number().min(0),
    children6: z.number().min(0),
    children4: z.number().min(0),
    children0: z.number().min(0),
  })
  .superRefine((arg, ctx) => {
    if (Object.values(arg).reduce((prev, curr) => prev + curr, 0) === 0) {
      ctx.addIssue({ message: "At least one passenger is mandatory", code: "custom" });
    }
  });

export type PassengerPickerData = z.infer<typeof passengerPickerData>;

export function getPassengersPresentation(
  passengers: PassengerPickerData,
  translator: Translator,
): string {
  return Object.entries(PASSENGER_DEFINITIONS)
    .map(([key]) => {
      const type = key as keyof PassengerPickerData;

      if (!passengers[type]) {
        return undefined;
      }

      return `${passengers[type]} ${getPassengerFullLabel(type, translator, passengers[type])}`;
    })
    .filter(ensureDefined)
    .join(", ");
}

export function getDefaultValue(): PassengerPickerData {
  return {
    adults: 1,
    children0: 0,
    children4: 0,
    children6: 0,
    seniors60: 0,
    seniors65: 0,
    youths12: 0,
    youths15: 0,
  };
}
