<script lang="ts">
  import Icon from "$lib/components/icons/icon.svelte";
  import LoadingIcon from "$lib/components/icons/loading-icon.svelte";
  import AutocompleteField from "$lib/components/ui/autocomplete-field.svelte";
  import DatePicker from "$lib/components/ui/date-picker/date-picker.svelte";
  import { formatPlace } from "$lib/formatting/location";
  import { slideFade } from "$lib/transitions/slide-fade";
  import { writable, type Writable } from "svelte/store";
  import { createEventDispatcher } from "svelte";
  import { z } from "zod";
  import integrationInstancesClient from "~/integration-instances-client";
  import {
    carSearchDataModel,
    type CarSearchDataError,
    type PartialCarSearchData,
    type CarSearchData,
  } from "../booking-flow";

  const dispatch = createEventDispatcher<{
    search: { data: CarSearchData; pending: Writable<boolean> };
  }>();
  const pending = writable(false);

  let differentDropoff = false;
  $: if (differentDropoff) {
    // Reset destination when different dropoff toggles to true
    data.destination = undefined;
  }

  export let data: PartialCarSearchData = {};

  let errors: CarSearchDataError | undefined;

  function search(): void {
    if ($pending) {
      return;
    }

    try {
      dispatch("search", {
        data: carSearchDataModel.parse({
          ...data,
          destination: differentDropoff ? data.destination : data.origin,
        }),
        pending,
      });
    } catch (err) {
      if (err instanceof z.ZodError) {
        errors = err.format();

        if (!differentDropoff) {
          clearError("destination");
        }
      }
    }
  }

  function clearError(error: keyof CarSearchData): void {
    if (errors) {
      delete errors[error];
    }

    errors = errors;
  }
</script>

<form
  class="car-search"
  on:submit|preventDefault={search}
  class:dropoff-different-location={differentDropoff}
>
  <AutocompleteField
    bind:value={data.origin}
    required
    label="Pick-up Location"
    placeholder="Enter pick-up location"
    autocomplete={integrationInstancesClient.mobile.places.find}
    formatter={formatPlace}
    error={errors?.origin?._errors}
  />

  {#if differentDropoff}
    <AutocompleteField
      bind:value={data.destination}
      required
      label="Drop-off Location"
      placeholder="Enter drop-off location"
      autocomplete={integrationInstancesClient.mobile.places.find}
      formatter={formatPlace}
      error={errors?.destination?._errors}
    />
  {/if}

  <DatePicker
    label="Pick-up"
    bind:value={data.pickup}
    required
    includeTime
    error={errors?.pickup?._errors}
  />
  <DatePicker
    label="Drop-off"
    bind:value={data.dropoff}
    required
    includeTime
    error={errors?.dropoff?._errors}
  />

  <button variant="primary">
    {#if $pending}
      <LoadingIcon />
    {:else}
      <Icon variant="search" size="20px" color="var(--color-common-dark-strong)" />
    {/if}
  </button>

  <div class="options" typography="body-medium">
    <label>
      <input type="checkbox" bind:checked={differentDropoff} />
      <span>Drop-off car in a different location</span>
    </label>

    <label class="age">
      <span>Driver's age:</span>
      <input
        type="number"
        bind:value={data.driverAge}
        typography="body-medium"
        on:input={clearError.bind(clearError, "driverAge")}
      />

      {#if errors?.driverAge?._errors}
        <span class="error" transition:slideFade={{ duration: 300 }}>
          {errors.driverAge._errors}
        </span>
      {/if}
    </label>
  </div>
</form>

<style>
  .car-search {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr max-content;
    gap: 19px 8px;
    align-items: flex-start;
    max-width: 1154px;
    padding: 24px;
    color: var(--color-common-light-strong);
    background: var(--color-common-background-light-main);
    border-radius: 16px;
    user-select: none;
  }

  .car-search.dropoff-different-location {
    grid-template-columns: 1fr 1fr 1fr 1fr max-content;
  }

  .car-search > :global(.autocomplete-field),
  .car-search > :global(.date-picker) {
    --label-font-size: 14px;
    --label-font-weight: 600;
    --label-font-family: "Inter";
  }

  .car-search > button[variant] {
    width: 56px;
    margin-top: 22px;
    padding-right: 16px;
    padding-left: 16px;
  }

  .options {
    display: flex;
    grid-column: 1 / -1;
    gap: 24px;
    align-items: flex-start;
  }

  .options > label {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 0 8px;
    align-items: center;
  }

  input[type="checkbox"] {
    margin: 0;
  }

  .age {
    margin-top: -5px;
  }

  .age > input {
    width: 70px;
    padding: 4px 8px;
    color: var(--color-common-light-strong);
    background-color: var(--color-common-background-light-main);
    border: var(--color-common-line-medium) 1px solid;
    border-radius: 4px;
    transition: border-color 200ms ease;
  }

  .age > input:focus {
    border-color: var(--color-common-line-strong);
    outline: 0;
  }

  .error {
    grid-column: 1 / -1;
    margin-top: 6px;
    color: #fe4e4e;
    font-weight: 400;
    font-size: 12px;
    font-family: Poppins, Arial, Helvetica, sans-serif;
    font-style: normal;
    line-height: 16px;
  }
</style>
