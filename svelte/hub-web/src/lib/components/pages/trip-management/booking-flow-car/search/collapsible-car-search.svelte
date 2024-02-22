<script lang="ts">
  import { getLocale } from "$lib/i18n";
  import type { CarSearchData } from "../car-search-data";
  import CollapsibleSearch from "../../collapsible-search.svelte";
  import CarSearch from "./car-search.svelte";

  export let searchData: CarSearchData;

  $: differentDropoff = searchData.origin.id !== searchData.destination.id;

  const locale = getLocale();
</script>

<CollapsibleSearch>
  <svelte:fragment slot="overview">
    <div typography="body-large" class="orig-dest" weight="bold">
      {searchData.origin.name}

      {#if differentDropoff}
        <span typography="label-medium" weight="bold">{"->"}</span>
        {searchData.destination.name}
      {/if}
    </div>

    <div typography="label-large">
      {searchData.pickup.toLocaleDateString($locale, {
        weekday: "short",
        day: "numeric",
        month: "short",
      })}
      -
      {searchData.dropoff.toLocaleDateString($locale, {
        weekday: "short",
        day: "numeric",
        month: "short",
      })}
      {#if differentDropoff}
        · Different drop-off
      {/if}
      · Driver's age: {searchData.driverAge}
    </div>
  </svelte:fragment>

  <CarSearch data={searchData} on:search />
</CollapsibleSearch>

<style>
  .orig-dest {
    display: flex;
    gap: 4px;
    align-items: center;
  }

  .orig-dest > span {
    color: var(--color-main-primary-500);
  }
</style>
