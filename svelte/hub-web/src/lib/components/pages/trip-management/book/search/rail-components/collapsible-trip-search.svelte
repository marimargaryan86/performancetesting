<script lang="ts">
  import { getPassengersPresentation } from "$lib/models/passenger";
  import { getLocale, getTranslator } from "$lib/i18n";
  import type { TripSearchData } from "../trip-search-data";
  import CollapsibleSearch from "../../../collapsible-search.svelte";
  import TripSearch from "./trip-search.svelte";

  export let searchData: TripSearchData;

  const locale = getLocale();
  const t = getTranslator();
</script>

<CollapsibleSearch>
  <svelte:fragment slot="overview">
    <div typography="body-large" class="orig-dest" weight="bold">
      {searchData.origin.name}
      <span typography="label-medium" weight="bold">{"->"}</span>
      {searchData.destination.name}
    </div>

    <div typography="label-large">
      {searchData.outbound.toLocaleDateString($locale, {
        weekday: "short",
        day: "numeric",
        month: "short",
      })}

      {#if searchData.tripType === "round-trip"}
        - {searchData.inbound.toLocaleDateString($locale, {
          weekday: "short",
          day: "numeric",
          month: "short",
        })}
      {/if}
      ·
      {$t(`tripTypes.${searchData.tripType}`)}
      ·
      {getPassengersPresentation(searchData.passengers, $t)}
    </div>
  </svelte:fragment>

  <TripSearch data={searchData} on:search />
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
