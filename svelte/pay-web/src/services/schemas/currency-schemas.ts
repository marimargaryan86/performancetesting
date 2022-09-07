import type { Identifier } from "./base-schemas";

export type CurrencyIdentifier = Identifier & {
  type: "currencies";
};
