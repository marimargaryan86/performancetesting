<script lang="ts" context="module">
  export const tripSearchQueryData = z.object({
    origin: z.string().uuid(),
    destination: z.string().uuid(),
    outbound: z.date({ coerce: true }),
    inbound: z.date({ coerce: true }).optional(),
    adults: z.number({ coerce: true }).min(1),
    children: z.number({ coerce: true }).min(0),
    infants: z.number({ coerce: true }).min(0),
  });

  export const tripSearchData = z.object({
    passengers: passengerPickerData,
    originId: z.string({ required_error: "Origin is mandatory" }).uuid(),
    destinationId: z.string({ required_error: "Destination is mandatory" }).uuid(),
    outbound: z.date({ required_error: "Departure date is mandatory" }),
    inbound: z.date().optional(),
  });

  type TripSearchDataInternal = z.infer<typeof tripSearchData>;

  export type TripSearchData = Omit<TripSearchDataInternal, "originId" | "destinationId"> & {
    origin: PlaceModel;
    destination: PlaceModel;
  };

  export type PartialTripSearchData = PartiallyPartial<TripSearchData, "passengers">;

  export function formatPlace(place?: PlaceModel): string {
    if (!place) {
      return "";
    }

    if (place.country.name) {
      return `${place.name}, ${place.country.name}`;
    }

    return place.name;
  }
</script>

<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import PassengerPicker, { passengerPickerData } from "./passenger-picker/passenger-picker.svelte";
  import routeConfig from "routeConfig";
  import Button from "components/ui/button.svelte";
  import { page } from "$app/stores";
  import AutocompleteField from "components/ui/autocomplete-field.svelte";
  import { callAction, type PartiallyPartial } from "utils/common";
  import { browser } from "$app/environment";
  import { createEventDispatcher } from "svelte";
  import { z } from "zod";
  import { URLExtended } from "utils/url";
  import SearchIcon from "components/icons/search-icon.svelte";
  import type { PlaceModel } from "integration/junction-mobile-api/schemas/place";

  export let data: PartialTripSearchData = {
    passengers: {
      adults: 1,
      children: 0,
      infants: 0,
    },
  };

  let errors: z.ZodFormattedError<TripSearchDataInternal> | undefined = undefined;

  const dispatch = createEventDispatcher<{ search: URL }>();

  async function listPlaces(query: string): Promise<PlaceModel[]> {
    if (!browser) {
      return [];
    }

    const result = await callAction<{ places: PlaceModel[] }>({
      action: routeConfig.tripManagement.book.actions.listPlaces,
      data: { query },
      apply: false,
    });

    return result.type === "success" ? result.data?.places ?? [] : [];
  }

  function search(): void {
    const parseResult = tripSearchData.safeParse({
      ...data,
      originId: data.origin?.id,
      destinationId: data.destination?.id,
    });

    if (!parseResult.success) {
      errors = parseResult.error.format();

      return;
    }

    errors = undefined;
    const parsedData = parseResult.data;

    dispatch(
      "search",
      new URLExtended(routeConfig.tripManagement.book.select.root, {
        base: $page.url.origin,
        query: {
          outbound: parsedData.outbound.toLocaleDateString("sv-SE"),
          inbound: parsedData.inbound?.toLocaleDateString("sv-SE"),
          origin: parsedData.originId,
          destination: parsedData.destinationId,
          ...parsedData.passengers,
        },
        querySchema: tripSearchQueryData,
      }),
    );
  }
</script>

<form class="trip-search" on:submit|preventDefault={search}>
  <AutocompleteField
    label="From"
    required
    placeholder="City or Station"
    bind:value={data.origin}
    autocomplete={listPlaces}
    formatter={formatPlace}
    error={errors?.originId?._errors}
    clearable
  />
  <AutocompleteField
    label="To"
    required
    placeholder="City or Station"
    bind:value={data.destination}
    autocomplete={listPlaces}
    formatter={formatPlace}
    error={errors?.destinationId?._errors}
    clearable
  />

  <DatePicker
    range={false}
    label="Depart"
    bind:value={data.outbound}
    id="depart-date"
    placeholder="Add date"
    error={errors?.outbound?._errors}
    required
  />

  <Button on:click={search}>
    <SearchIcon color="var(--color-common-dark-strong)" />
  </Button>

  <PassengerPicker
    bind:passengers={data.passengers}
    error={errors?.passengers?.adults?._errors ??
      errors?.passengers?.children?._errors ??
      errors?.passengers?.infants?._errors}
  />
</form>

<style>
  .trip-search {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr min-content;
    gap: 8px;
    align-items: flex-start;
    max-width: 1154px;
    padding: 24px 24px 16px;
    background: var(--color-common-background-light-main);
    border-radius: 16px;
  }

  .trip-search > :global(.autocomplete-field),
  .trip-search > :global(.date-picker) {
    --label-font-size: 14px;
    --label-font-weight: 600;
    --label-font-family: "Inter";
  }

  .trip-search > :global(button) {
    margin-top: 22px;
  }
</style>
