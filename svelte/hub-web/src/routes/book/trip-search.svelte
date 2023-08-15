<script lang="ts" context="module">
  export type TripSearchData = {
    passengers: PassengerPickerData;
    origin: PlaceModel;
    destination: PlaceModel;
    outbound: Date;
    inbound?: Date;
  };

  export type PartialTripSearchData = Omit<Partial<TripSearchData>, "passengers"> & {
    passengers: PassengerPickerData;
  };

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
  import SearchIcon from "components/icons/book-search-icon.svelte";
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import PassengerPicker, {
    type PassengerPickerData,
  } from "./passenger-picker/passenger-picker.svelte";
  import routeConfig from "routeConfig";
  import Button from "components/ui/button.svelte";
  import { page } from "$app/stores";
  import AutocompleteField from "components/ui/autocomplete-field.svelte";
  import type { PlaceModel } from "models/booking/location";
  import { callAction } from "utils/common";
  import { browser } from "$app/environment";
  import { createEventDispatcher } from "svelte";

  export let data: PartialTripSearchData = {
    passengers: {
      adults: 1,
      children: 0,
      infants: 0,
    },
  };

  const dispatch = createEventDispatcher<{ search: URL }>();

  function getSearchQuery(nextData: PartialTripSearchData): URL {
    if (!formValid(nextData)) {
      throw new Error("Invalid search data");
    }

    const url = new URL(routeConfig.book.select.root, $page.url.origin);

    url.searchParams.set("origin", nextData.origin.id);
    url.searchParams.set("destination", nextData.destination.id);

    if (nextData.passengers.adults) {
      url.searchParams.set("adults", nextData.passengers.adults.toString());
    }

    if (nextData.passengers.children) {
      url.searchParams.set("children", nextData.passengers.children.toString());
    }

    if (nextData.passengers.infants) {
      url.searchParams.set("infants", nextData.passengers.infants.toString());
    }

    if (nextData.outbound) {
      url.searchParams.set("outbound", nextData.outbound.toLocaleDateString("sv-SE"));
    }

    return url;
  }

  async function listPlaces(query: string): Promise<PlaceModel[]> {
    if (!browser) {
      return [];
    }

    const result = await callAction<{ places: PlaceModel[] }>({
      action: routeConfig.book.actions.listPlaces,
      data: { query },
      apply: false,
    });

    return result.type === "success" ? result.data?.places ?? [] : [];
  }

  function search(): void {
    try {
      dispatch("search", getSearchQuery(data));
    } catch {
      //
    }
  }

  function formValid(nextData: PartialTripSearchData): nextData is TripSearchData {
    return Boolean(
      nextData.origin &&
        nextData.destination &&
        nextData.outbound &&
        (nextData.passengers.adults ?? 0) > 0,
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
    clearable
  />
  <AutocompleteField
    label="To"
    required
    placeholder="City or Station"
    bind:value={data.destination}
    autocomplete={listPlaces}
    formatter={formatPlace}
    clearable
  />

  <DatePicker
    range={false}
    label="Depart"
    bind:value={data.outbound}
    id="depart-date"
    placeholder="Add date"
    required
  />

  <Button on:click={search}>
    <SearchIcon color="var(--color-common-dark-strong)" />
  </Button>

  <PassengerPicker bind:passengers={data.passengers} />
</form>

<style>
  .trip-search {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr min-content;
    gap: 8px;
    align-items: flex-end;
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
</style>
