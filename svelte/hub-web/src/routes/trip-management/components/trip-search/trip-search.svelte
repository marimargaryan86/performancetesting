<script lang="ts" context="module">
  export function formatPlace(place?: Place): string {
    if (!place) {
      return "";
    }

    return [place.name, place.mainCity, place.country.name].filter(ensureDefined).join(", ");
  }

  function getPrecision(place: Place): "precise" | undefined {
    if (place.types.includes("city") || place.types.includes("unspecified")) {
      return undefined;
    }

    return "precise";
  }
</script>

<script lang="ts">
  import DatePicker from "components/ui/date-picker/date-picker.svelte";
  import PassengerPicker from "./passenger-picker/passenger-picker.svelte";
  import Button from "components/ui/button.svelte";
  import AutocompleteField from "components/ui/autocomplete-field.svelte";
  import { z } from "zod";
  import SearchIcon from "components/icons/search-icon.svelte";
  import SwapIcon from "components/icons/swap-icon.svelte";
  import type { Place } from "integration/junction-mobile-api/schemas/place";
  import LoadingIcon from "components/icons/loading-icon.svelte";
  import { goto } from "$app/navigation";
  import type { DateRange } from "models/date-time";
  import { addToDate, getZeroTimeDate } from "utils/date-time";
  import tripManagement, {
    type SearchDataModel,
  } from "../../../integration/trip-management/trip-management";
  import routeConfig from "routeConfig";
  import integrationInstancesClient from "integration-instances-client";
  import { ensureDefined } from "utils/array";
  import { writable } from "svelte/store";

  export let data: Partial<SearchDataModel> = {};
  export let origin: Place | undefined = undefined;
  export let destination: Place | undefined = undefined;
  let isSwapIconRotated = false;
  let isSwapIconStandard = true;

  let passengers: SearchDataModel["passengers"] = data.passengers ?? {
    seniors65: 0,
    seniors60: 0,
    adults: 1,
    youths15: 0,
    youths12: 0,
    children6: 0,
    children4: 0,
    children0: 0,
  };
  let errors: z.ZodFormattedError<SearchDataModel> | undefined = undefined;
  let dateSpan: DateRange = {
    from: getZeroTimeDate(new Date()),
    to: getZeroTimeDate(addToDate(new Date(), { years: 1 })),
  };

  const pending = writable(false);

  $: data = {
    ...data,
    origin: origin
      ? { id: origin.id, ...origin.coordinates, precision: getPrecision(origin) }
      : undefined,
    destination: destination
      ? { id: destination.id, ...destination.coordinates, precision: getPrecision(destination) }
      : undefined,
    passengers,
    timeZoneOffset: data.outbound?.getTimezoneOffset() ?? 0,
  };

  function swapOriginAndDestination(): void {
    isSwapIconRotated = !isSwapIconRotated;
    isSwapIconStandard = !isSwapIconStandard;
    [origin, destination] = [destination, origin];
  }

  async function search(): Promise<void> {
    if ($pending) {
      return;
    }

    try {
      $pending = true;

      await tripManagement.search(data);

      await goto(routeConfig.routes.tripManagement.routes.book.routes.select.root, {
        invalidateAll: true,
      });
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = err.format();
      }
    } finally {
      $pending = false;
    }
  }
</script>

<form class="trip-search" on:submit|preventDefault={search}>
  <AutocompleteField
    label="From"
    required
    placeholder="City or Station"
    bind:value={origin}
    autocomplete={integrationInstancesClient.mobile.places.find}
    formatter={formatPlace}
    error={errors?.origin?._errors}
    clearable
  />

  <Button class="swap-btn" variant="text" on:click={swapOriginAndDestination}>
    <SwapIcon rotate={isSwapIconRotated} standard={isSwapIconStandard} />
  </Button>

  <AutocompleteField
    label="To"
    required
    placeholder="City or Station"
    bind:value={destination}
    autocomplete={integrationInstancesClient.mobile.places.find}
    formatter={formatPlace}
    error={errors?.destination?._errors}
    clearable
  />

  <DatePicker
    label="Depart"
    bind:value={data.outbound}
    id="depart-date"
    placeholder="Add date"
    error={errors?.outbound?._errors}
    span={dateSpan}
    required
  />

  <Button on:click={search}>
    {#if $pending}
      <LoadingIcon />
    {:else}
      <SearchIcon color="var(--color-common-dark-strong)" />
    {/if}
  </Button>

  <PassengerPicker bind:passengers error={errors?.passengers?._errors} />
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

  .trip-search > :global(.autocomplete-field),
  .trip-search > :global(.date-picker) {
    --label-font-size: 14px;
    --label-font-weight: 600;
    --label-font-family: "Inter";
  }

  .trip-search > :global(button) {
    margin-top: 22px;
    padding-right: 16px;
    padding-left: 16px;
  }

  :global(.swap-btn) {
    --icon-size: 27px;
  }
</style>
