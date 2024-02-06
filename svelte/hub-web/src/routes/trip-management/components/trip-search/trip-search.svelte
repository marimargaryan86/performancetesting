<script lang="ts" context="module">
  export const SEARCH_WINDOW_H = 2;
  export const SEARCH_WINDOW_DELTA_MS = 3600000 * SEARCH_WINDOW_H;

  const searchDataBaseModel = z.object({
    origin: z.object(placeModel.shape, { required_error: "Origin is mandatory" }),
    destination: z.object(placeModel.shape, { required_error: "Destination is mandatory" }),
    passengers: passengerPickerData,
    windowH: z.number().min(0).default(SEARCH_WINDOW_H),
    outbound: z
      .date({ coerce: true, required_error: "Departure date is mandatory" })
      .refine((value) => value >= new Date(), "Departure date can't be in the past"),
  });

  type RequiredFields = keyof Pick<SearchData, "tripType" | "passengers">;
  const searchDataOneWayModel = searchDataBaseModel.extend({
    tripType: z.literal("one-way" satisfies TripType),
  });
  type SearchDataOneWay = z.infer<typeof searchDataOneWayModel>;
  type PartialSearchDataOneWay = Partial<Omit<SearchDataOneWay, RequiredFields>> &
    Pick<SearchDataOneWay, RequiredFields>;

  const searchDataRoundTripModel = searchDataBaseModel.extend({
    tripType: z.literal("round-trip" satisfies TripType),
    outbound: z
      .date({ coerce: true, required_error: "Outbound date is mandatory" })
      .refine((value) => value > new Date(), "Outbound date can't be in the past"),
    inbound: z.date({ coerce: true, required_error: "Inbound date is mandatory" }),
  });
  type SearchDataRoundTrip = z.infer<typeof searchDataRoundTripModel>;
  type PartialSearchDataRoundTrip = Partial<Omit<SearchDataRoundTrip, RequiredFields>> &
    Pick<SearchDataRoundTrip, RequiredFields>;

  export const searchDataModel = z
    .discriminatedUnion("tripType", [searchDataOneWayModel, searchDataRoundTripModel])
    .refine((value) => value.tripType !== "round-trip" || value.inbound > value.outbound, {
      message: "Inbound date must be after outbound date",
      path: ["inbound"],
    });
  export type SearchData = z.infer<typeof searchDataModel>;
  export type PartialSearchData = PartialSearchDataOneWay | PartialSearchDataRoundTrip;

  export type SearchDataError = z.ZodFormattedError<SearchData>;

  export function formatPlace(place?: Place): string {
    if (!place) {
      return "";
    }

    return [place.name, place.mainCity, place.country.name].filter(ensureDefined).join(", ");
  }
</script>

<script lang="ts">
  import { dev } from "$app/environment";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import PassengerPicker, {
    getDefaultValue,
    passengerPickerData,
  } from "./passenger-picker/passenger-picker.svelte";
  import TripTypePicker, { type TripType } from "./trip-type-picker.svelte";
  import AutocompleteField from "components/ui/autocomplete-field.svelte";
  import SwapIcon from "components/icons/swap-icon.svelte";
  import { placeModel, type Place } from "integration/junction-mobile-api/schemas/place";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import integrationInstancesClient from "integration-instances-client";
  import { ensureDefined } from "utils/array";
  import { writable, type Writable } from "svelte/store";
  import { getLocaleData } from "i18n";
  import Icon from "components/icons/icon.svelte";
  import { createEventDispatcher } from "svelte";
  import { z } from "zod";

  export let data: PartialSearchData = {
    tripType: "one-way",
    passengers: getDefaultValue(),
  };
  let errors: SearchDataError | undefined = undefined;

  const dispatch = createEventDispatcher<{
    search: { data: SearchData; pending: Writable<boolean> };
  }>();
  const pending = writable(false);
  const i18n = getLocaleData();
  const today = new Date();
  today.setSeconds(0);
  today.setMinutes(0);

  function swapOriginAndDestination(): void {
    [data.origin, data.destination] = [data.destination, data.origin];
  }

  function search(): void {
    try {
      dispatch("search", { data: searchDataModel.parse(data), pending });
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = err.format();
      }
    }
  }
</script>

<form
  class="trip-search"
  class:extended={data.tripType === "round-trip"}
  on:submit|preventDefault={search}
>
  <AutocompleteField
    label={$i18n.words.from}
    required
    placeholder={$i18n.sentences.cityOrStation}
    bind:value={data.origin}
    autocomplete={integrationInstancesClient.mobile.places.find}
    formatter={formatPlace}
    error={errors?.origin?._errors}
    clearable
  />

  <button type="button" tabindex="-1" class="swap" on:click={swapOriginAndDestination}>
    <SwapIcon />
  </button>

  <AutocompleteField
    label={$i18n.words.to}
    required
    placeholder={$i18n.sentences.cityOrStation}
    bind:value={data.destination}
    autocomplete={integrationInstancesClient.mobile.places.find}
    formatter={formatPlace}
    error={errors?.destination?._errors}
    clearable
  />

  <DatePicker
    label={data.tripType === "one-way" ? $i18n.words.depart : $i18n.words.outbound}
    bind:value={data.outbound}
    error={errors?.outbound?._errors}
    required
    min={today}
    includeTime
  />

  {#if data.tripType === "round-trip"}
    <DatePicker
      label={$i18n.words.inbound}
      bind:value={data.inbound}
      error={errors && "inbound" in errors ? errors.inbound?._errors : undefined}
      required
      min={today}
      includeTime
    />
  {/if}

  <button variant="primary">
    {#if $pending}
      <LoadingIcon />
    {:else}
      <Icon variant="search" size="20px" color="var(--color-common-dark-strong)" />
    {/if}
  </button>

  <div class="settings">
    {#if dev}
      <TripTypePicker bind:value={data.tripType} />
    {/if}

    <PassengerPicker bind:passengers={data.passengers} error={errors?.passengers?._errors} />
  </div>
</form>

<style>
  .trip-search {
    display: grid;
    grid-template-columns: 1fr max-content 1fr 1fr max-content;
    gap: 8px;
    align-items: flex-start;
    max-width: 1154px;
    padding: 24px 24px 16px;
    background: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .trip-search.extended {
    grid-template-columns: 1fr max-content 1fr 1fr 1fr max-content;
  }

  .trip-search > :global(.autocomplete-field),
  .trip-search > :global(.date-picker) {
    --label-font-size: 14px;
    --label-font-weight: 600;
    --label-font-family: "Inter";
  }

  .settings {
    display: flex;
    grid-column: 1 / -1;
    gap: 24px;
  }

  .trip-search > button[variant] {
    margin-top: 22px;
    padding-right: 16px;
    padding-left: 16px;
  }

  .trip-search > button.swap {
    margin-top: 36px;
    padding: 0;
    background-color: transparent;
    border: 0;
    cursor: pointer;
  }
</style>
