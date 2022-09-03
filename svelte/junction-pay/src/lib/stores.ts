import type { CurrencyModel } from "$integration/currency-cloud/models/currencies";
import type { CountryModel } from "$models/location-models";
import type { ModalParams } from "$models/modal-models";
import instances from "$services/instances";
import { readable, writable } from "svelte/store";

export const currencyStore = readable<Promise<CurrencyModel[]>>(instances.currency.find());

export const countryStore = readable<Promise<CountryModel[]>>(instances.countries.find());

export const modal = writable<ModalParams>({
  status: "closed", // opened | closed,
  type: "info",
  component: undefined,
  title: "",
  options: {},
});

export function openPopup(params: ModalParams): void {
  modal.set({
    ...params,
    status: "open",
  });
}

export function close() {
  modal.set({
    status: "closed",
    type: "modal",
    title: "",
    component: undefined,
    options: {},
    firstFocusElement: undefined,
  });
}
