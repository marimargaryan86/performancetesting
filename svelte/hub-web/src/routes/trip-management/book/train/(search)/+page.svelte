<script lang="ts">
  import { getPageTitle } from "$lib/utils/page-title";
  import TripSearch from "$lib/components/pages/trip-management/booking-flow-train/trip-search/trip-search.svelte";
  import { getTranslator } from "$lib/i18n";
  import type { ComponentEvents } from "svelte";
  import { manager } from "$lib/components/pages/trip-management/booking-flow-train/booking-flow";
  import { goto } from "$app/navigation";
  import routeConfig from "$lib/route-config";

  const t = getTranslator();

  async function search(event: ComponentEvents<TripSearch>["search"]): Promise<void> {
    event.detail.pending?.set(true);
    await manager.search(event.detail.data);
    await goto(routeConfig.routes.tripManagement.routes.book.routes.train.routes.select.root);
    event.detail.pending?.set(false);
  }
</script>

<svelte:head>
  <title>
    {getPageTitle(
      $t("title"),
      $t("pages.tripManagement.title"),
      $t("pages.tripManagement.pages.book.title"),
      $t("pages.tripManagement.pages.book.pages.search.title"),
    )}
  </title>
</svelte:head>

<div class="search-wrapper">
  <TripSearch on:search={search} />
</div>

<style>
  .search-wrapper {
    padding: 24px;
  }
</style>
