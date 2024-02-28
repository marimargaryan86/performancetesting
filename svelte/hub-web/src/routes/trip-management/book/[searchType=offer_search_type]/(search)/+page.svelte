<script lang="ts">
  import TripSearch from "$lib/components/pages/trip-management/book/search/rail-components/trip-search.svelte";
  import { getTranslator } from "$lib/i18n";
  import type { ComponentEvents } from "svelte";
  import { manager } from "$lib/booking-manager/booking-manager";
  import { goto } from "$app/navigation";
  import routeConfig from "$lib/route-config";
  import { Feature, getFeatureTools } from "$lib/utils/feature-flags";
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import SearchTabs from "$lib/components/pages/trip-management/search-tabs.svelte";
  import CarSearch from "$lib/components/pages/trip-management/book/search/car-components/car-search.svelte";

  export let data;

  const featureTools = getFeatureTools();
  const t = getTranslator();

  async function search(event: ComponentEvents<TripSearch>["search"]): Promise<void> {
    event.detail.pending?.set(true);
    await manager.search(
      event.detail.data,
      data.searchType === "rail" && $featureTools.hasFeature(Feature.OFFERS_TIME_WINDOWS),
    );
    await goto(
      routeConfig.routes.tripManagement.routes.book.routes[data.searchType].routes.select.root,
    );
    event.detail.pending?.set(false);
  }
</script>

<BookingLayout
  pageTitle={$t(`pages.tripManagement.pages.book.pages.${data.searchType}.pages.search.title`)}
  pageSubTitle={$t(
    `pages.tripManagement.pages.book.pages.${data.searchType}.pages.search.subTitle`,
  )}
>
  <div class="search-wrapper">
    {#if $featureTools.hasFeature(Feature.CAR_RENTAL)}
      <SearchTabs active={data.searchType} />
    {/if}

    {#if data.searchType === "rail"}
      <TripSearch on:search={search} />
    {:else if data.searchType === "car"}
      <CarSearch on:search={search} />
    {/if}
  </div>
</BookingLayout>

<style>
  .search-wrapper {
    display: flex;
    flex-flow: column;
    gap: 16px;
    max-width: 1154px;
    margin: 24px;
    padding: 16px 24px;
    background: var(--color-common-background-light-main);
    border-radius: 16px;
  }
</style>
