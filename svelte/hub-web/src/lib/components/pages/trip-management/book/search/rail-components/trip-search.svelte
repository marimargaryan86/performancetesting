<script lang="ts">
  import DatePicker from "$lib/components/ui/date-picker/date-picker.svelte";
  import PassengerPicker from "./passenger-picker/passenger-picker.svelte";
  import { getDefaultValue } from "$lib/models/passenger";
  import AutocompleteField from "$lib/components/ui/autocomplete-field.svelte";
  import SwapIcon from "$lib/components/icons/swap-icon.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import integrationInstancesClient from "~/integration-instances-client";
  import { writable, type Writable } from "svelte/store";
  import { getTranslator } from "$lib/i18n";
  import Icon from "$lib/components/icons/icon.svelte";
  import { createEventDispatcher } from "svelte";
  import { z } from "zod";
  import TripTypePicker from "./trip-type-picker.svelte";
  import {
    searchDataModel,
    type PartialTripSearchData,
    type TripSearchDataError,
    tripSearchDataParser,
  } from "../trip-search-data";
  import { formatPlace } from "$lib/formatting/location";
  import { getClosestFullHour } from "$lib/utils/date-time";
  import type { SearchData } from "$lib/booking-manager/booking-manager";
  import { Feature, getFeatureTools } from "$lib/utils/feature-flags";

  const featureTools = getFeatureTools();
  const dispatch = createEventDispatcher<{
    search: { data: SearchData; pending: Writable<boolean> };
  }>();
  const pending = writable(false);
  const t = getTranslator();
  const today = new Date();
  today.setSeconds(0);
  today.setMinutes(0);

  export let data: PartialTripSearchData = {
    tripType: $featureTools.hasFeature(Feature.ROUND_TRIP) ? "round-trip" : "one-way",
    passengers: getDefaultValue(),
    outbound: getClosestFullHour(new Date(), true),
  };
  let errors: TripSearchDataError | undefined = undefined;

  function swapOriginAndDestination(): void {
    [data.origin, data.destination] = [data.destination, data.origin];
  }

  function search(): void {
    try {
      dispatch("search", {
        data: tripSearchDataParser.toSearchData(searchDataModel.parse(data)),
        pending,
      });
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
  <div class="settings">
    {#if $featureTools.hasFeature(Feature.ROUND_TRIP)}
      <TripTypePicker bind:value={data.tripType} />
    {/if}

    <PassengerPicker bind:passengers={data.passengers} error={errors?.passengers?._errors} />
  </div>

  <AutocompleteField
    label={$t("words.from")}
    required
    placeholder={$t("sentences.cityOrStation")}
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
    label={$t("words.to")}
    required
    placeholder={$t("sentences.cityOrStation")}
    bind:value={data.destination}
    autocomplete={integrationInstancesClient.mobile.places.find}
    formatter={formatPlace}
    error={errors?.destination?._errors}
    clearable
  />

  <DatePicker
    label={data.tripType === "one-way" ? $t("words.depart") : $t("words.outbound")}
    bind:value={data.outbound}
    error={errors?.outbound?._errors}
    required
    min={today}
    includeTime
  />

  {#if data.tripType === "round-trip"}
    <DatePicker
      label={$t("words.inbound")}
      bind:value={data.inbound}
      error={errors && "inbound" in errors ? errors.inbound?._errors : undefined}
      required
      min={data.outbound}
      externalPlaceholder={data.outbound}
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
</form>

<style>
  .trip-search {
    display: grid;
    grid-template-columns: 1fr max-content 1fr 1fr max-content;
    gap: 16px 8px;
    align-items: flex-start;
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
    align-items: flex-start;
  }

  .trip-search > button[variant] {
    width: 56px;
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
