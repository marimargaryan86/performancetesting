<script lang="ts">
  import { goto } from "$app/navigation";
  import { manager } from "$lib/booking-manager/booking-manager";
  import CarSearch from "$lib/components/pages/trip-management/booking-flow-car/search/car-search.svelte";
  import BookingLayout from "$lib/components/pages/trip-management/booking-layout.svelte";
  import SearchTabs from "$lib/components/pages/trip-management/search-tabs.svelte";
  import { getTranslator } from "$lib/i18n";
  import routeConfig from "$lib/route-config";
  import { Feature, getFeatureTools } from "$lib/utils/feature-flags";
  import type { ComponentEvents } from "svelte";

  const featureTools = getFeatureTools();
  const t = getTranslator();

  async function search(event: ComponentEvents<CarSearch>["search"]): Promise<void> {
    event.detail.pending.set(true);
    try {
      await manager.search(event.detail.data, false);
      await goto(routeConfig.routes.tripManagement.routes.book.routes.car.routes.select.root);
    } finally {
      event.detail.pending.set(false);
    }
  }
</script>

<BookingLayout
  pageTitle={$t("pages.tripManagement.pages.book.pages.car.pages.search.title")}
  pageSubTitle={$t("pages.tripManagement.pages.book.pages.car.pages.search.subTitle")}
>
  <div class="search-wrapper">
    {#if $featureTools.hasFeature(Feature.CAR_RENTAL)}
      <SearchTabs active="car" />
    {/if}

    <CarSearch on:search={search} />
  </div>
</BookingLayout>

<style>
  .search-wrapper {
    display: flex;
    flex-flow: column;
    gap: 24px;
    max-width: 1154px;
    margin: 24px;
    padding: 16px 24px 24px;
    background: var(--color-common-background-light-main);
    border-radius: 16px;
  }
</style>
